import spacy
from spacy.matcher import Matcher
import re

nlp = spacy.load('en_core_web_trf')
matcher = Matcher(nlp.vocab)

def redact_phone_numbers(text):
    def find_phone_numbers(text):
        phone_numbers = []
        temp_num_str = ""
        temp_start = 0
        
        for i in range(len(text)):
            ch = text[i]
            if ch.isdigit() or ch in "+(":
                if temp_num_str == "":
                    temp_start = i
                if ch.isdigit():
                    temp_num_str += ch
            elif ch in " -().":
                continue
            else:
                if 7 <= len(temp_num_str) <= 15:
                    phone_numbers.append((temp_start, i))
                temp_num_str = ""
        
        if 7 <= len(temp_num_str) <= 15:
            phone_numbers.append((temp_start, len(text)))
        
        return phone_numbers
    
    phone_numbers = find_phone_numbers(text)
    phone_numbers.sort(reverse=True)
    
    for start, end in phone_numbers:
        text = text[:start] + '[PHONE_NUMBER]' + text[end:]
    
    return text

def redact_addresses(text):
    def find_unit_numbers(text):
        pattern = r'#\d{2}[-\s]?\d{1,3}'
        matches = re.finditer(pattern, text)
        result = [(match.start(), match.end()) for match in matches]
        return result
    
    def find_postal_codes(text):
        pattern = r'(Singapore\s\d{6})|(S\d{6})|(S\(\d{6}\))'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        result = [(match.start(), match.end()) for match in matches]
        return result
    
    matches = find_unit_numbers(text)
    matches += find_postal_codes(text)
        
    matches.sort(reverse=True)
    
    for start, end in matches:
        text = text[:start] + '[ADDRESS]' + text[end+1:]

    return text


def redact_entities_spacy(text):
    patterns = {
        'NAME': [
            [
                {'ENT_TYPE': 'PERSON'}
            ]
        ],
        'NRIC': [
            [
                {"TEXT": {"REGEX": "^[sStT]\d{7}[a-zA-Z]$"}}
            ]
        ],
        'PASSPORT': [
            [
                {"TEXT": {"REGEX": "^[eE]\\d{7}[a-zA-Z]$"}} # SG only
            ]
        ],
        'EMAIL': [
            [
                {'LIKE_EMAIL': True}
            ]
        ],
    }

    for label, pattern in patterns.items():
        matcher.add(label, pattern)

    doc = nlp(text)
    redacted_text = []
    last_end = 0

    matches = matcher(doc)
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        redacted_text.append(doc[last_end:start].text)
        redacted_text.append(f"[{label}]")
        last_end = end

    redacted_text.append(doc[last_end:].text)
    redacted_text = ''.join(redacted_text)

    return redacted_text

def combine_placeholders(text, placeholder):
    combined = re.sub(rf'(\[{placeholder}\])(\s*\[{placeholder}\])+', rf'[{placeholder}]', text)
    return combined

def redact_text(text):
    redacted_text_spacy = redact_entities_spacy(text)
    redacted_text_wo_address = redact_addresses(redacted_text_spacy)
    redacted_text_wo_phone_num = redact_phone_numbers(redacted_text_wo_address)
    final_redacted_text = combine_placeholders(redacted_text_wo_phone_num, 'NAME')
    final_redacted_text = combine_placeholders(final_redacted_text, 'ADDRESS')

    return final_redacted_text

text = "my name is tian chu and my nric is t0208761d and my phone number is 91234567 and passport is e1234567d and email is chulintian@gmail.com and my address is 423 hougang avenue 6 #06-106 s(530423)"
redacted_text = redact_text(text)
print(redacted_text)
