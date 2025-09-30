# Enhanced Field Recognition and Threading System

## Overview

The Thinkerbell system has been enhanced with comprehensive threading around name, state, and value recognition to ensure the model always selects the correct input fields when parsing and generating legal documents.

## Key Improvements

### 1. Multi-Pass Entity Extraction

The system now uses a three-pass approach:

1. **First Pass**: Extract all potential entities and build threading context
2. **Second Pass**: Apply threading logic to ensure consistency across related fields
3. **Third Pass**: Validate and cross-reference entities for accuracy

### 2. Enhanced Field Structure

Extended field recognition to include:

```python
{
    'brand_name': '[BRAND NAME]',
    'client_name': '[CLIENT NAME]',
    'partner_name': '[PARTNER NAME]',
    'influencer_name': '[INFLUENCER NAME]',
    'creator_name': '[CREATOR NAME]',
    'company_name': '[COMPANY NAME]',
    'state': '[STATE]',           # NEW
    'country': '[COUNTRY]',       # NEW
    'city': '[CITY]',            # NEW
    'contact_person': '[CONTACT PERSON]',  # NEW
    'email': '[EMAIL]',          # NEW
    'phone': '[PHONE]',          # NEW
    'address': '[ADDRESS]',      # NEW
    'abn': '[ABN]',             # NEW - Australian Business Number
    'acn': '[ACN]',             # NEW - Australian Company Number
    'duration': '[DURATION]',
    'compensation': '[COMPENSATION]',
    'platforms': '[PLATFORMS]',
    'deliverables': '[DELIVERABLES]'
}
```

### 3. Entity Threading System

Implemented comprehensive threading across five categories:

- **Companies**: Links brand_name, company_name, client_name
- **Individuals**: Links influencer_name, creator_name, partner_name, contact_person
- **Locations**: Links state, city, country, address with validation
- **Contacts**: Links email, phone, contact_person
- **Legal Entities**: Links ABN, ACN with company information

### 4. Australian-Focused Location Recognition

#### State/Territory Detection
- Recognizes all Australian states and territories (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
- Handles both abbreviations and full names
- Automatically sets country to "Australia" when Australian locations detected

#### City Recognition
- Comprehensive list of Australian major cities and suburbs
- Context-aware extraction from addresses and location references

#### Address Parsing
- Australian address format recognition
- Level/Suite, Street number, Street name, Suburb, State, Postcode patterns

### 5. Enhanced Company Name Recognition

#### New Patterns Added
- CLIENT/BRAND keyword patterns
- Full company suffix recognition (Pty Ltd, Australia Pty Ltd, etc.)
- Legal document patterns (BETWEEN CompanyName)
- Direct company suffix matching

#### Validation
- Length validation (2-50 characters)
- Exclusion of common non-company words
- Proper capitalization requirements
- Company suffix detection vs individual name validation

### 6. Contact Information Extraction

#### Email Recognition
- Standard email pattern matching
- First email found is used as primary contact

#### Australian Phone Numbers
- +61 international format
- 04xx xxx xxx mobile format
- (0x) xxxx xxxx landline format
- 0x xxxx xxxx standard format

#### Contact Person Extraction
- Manager/Agent/Representative title patterns
- Name-title association patterns
- Validation for reasonable name length (1-3 words)

### 7. Legal Identifier Recognition

#### Australian Business Number (ABN)
- Pattern: ABN XX XXX XXX XXX or ABN XXXXXXXXXXX
- Automatic spacing normalization

#### Australian Company Number (ACN)
- Pattern: ACN XXX XXX XXX or ACN XXXXXXXXX
- Automatic spacing normalization

### 8. Cross-Field Threading Logic

#### Company Threading
- If brand_name is found, automatically populate company_name and client_name if empty
- Ensures consistency across all company-related fields

#### Individual Threading
- If influencer_name is found, populate creator_name and partner_name if empty
- Maintains consistency for person references throughout document

#### Location Threading
- State detection automatically sets country to Australia for Australian states
- City and state information is cross-validated for consistency
- Address information is used to populate city and state if not already found

### 9. Entity Validation and Consistency Checking

#### Company Name Validation
- Reasonable length checks (2-50 characters)
- Exclusion of common non-company words
- Proper capitalization requirements

#### Individual Name Validation
- 1-4 word limit for individual names
- Exclusion of company suffixes from individual names
- Proper capitalization validation

#### Location Consistency
- Australian state validation automatically sets country
- Cross-reference validation between city, state, and country

### 10. Threaded Entity References in Generation

#### Smart Entity Resolution
- `_build_threaded_entity_reference()` method provides fallback logic
- If primary field is empty, automatically uses related threaded fields
- Ensures no placeholder text appears in final generated documents

#### Location String Building
- `_build_threaded_location_string()` creates proper legal location references
- Handles full addresses, city/state combinations, or fallback to generic terms
- Australian corporation format compliance

## Usage Examples

### Input Document Processing
```python
# Example input with multiple entities
text = """
BETWEEN Thinkerbell Pty Ltd (ABN 99 618 397 658) of Level 4, 261-265 Chalmers Street, Redfern, NSW, 2016
AND Ross Andrewartha of Day Mgmt (ABN 77 623 893 345) of 99-101 Commercial Rd, South Yarra VIC 3141
CLIENT Barilla Australia Pty Ltd
CONTACT Joy Liu - Earned Thinker
Phone: +61 406 187 333
Email: joyliu@thinkerbell.com
FEE $5,175 to be paid
TERM 2 months
"""

# Enhanced extraction results:
{
    'brand_name': 'Thinkerbell Pty Ltd',
    'company_name': 'Thinkerbell Pty Ltd',  # Threaded from brand_name
    'client_name': 'Barilla Australia Pty Ltd',
    'influencer_name': 'Ross Andrewartha',
    'creator_name': 'Ross Andrewartha',     # Threaded from influencer_name
    'state': 'NSW',
    'country': 'Australia',                 # Auto-set from Australian state
    'city': 'Redfern',
    'contact_person': 'Joy Liu',
    'email': 'joyliu@thinkerbell.com',
    'phone': '+61 406 187 333',
    'address': 'Level 4, 261-265 Chalmers Street, Redfern, NSW, 2016',
    'abn': '99 618 397 658',
    'compensation': '$5,175',
    'duration': '2 months'
}
```

### Generated Document Output
The threaded entities ensure consistent, professional output:

```
This Influencer Marketing Agreement ('Agreement') is entered into between Thinkerbell Pty Ltd, a NSW corporation ('Company'), and Ross Andrewartha, an individual content creator ('Influencer').
```

## Benefits

1. **Accuracy**: Multi-pass extraction with validation ensures high accuracy
2. **Consistency**: Threading prevents mismatched entity references
3. **Completeness**: Comprehensive field coverage for Australian legal documents
4. **Reliability**: Fallback mechanisms ensure no placeholder text in output
5. **Maintainability**: Modular design allows easy pattern updates and extensions

## Technical Implementation

The enhanced system is implemented in the `ModelService` class with the following key methods:

- `_extract_key_information()`: Main extraction coordinator
- `_extract_all_entities()`: First pass entity extraction
- `_extract_location_information()`: Australian location parsing
- `_extract_contact_information()`: Contact detail extraction
- `_extract_address_information()`: Address parsing
- `_apply_entity_threading()`: Cross-field threading logic
- `_validate_entity_consistency()`: Final validation pass
- `_build_threaded_location_string()`: Location reference generation
- `_build_threaded_entity_reference()`: Entity reference with fallbacks

This comprehensive threading system ensures that the Thinkerbell model always selects the correct input fields and generates consistent, professional legal documents.
