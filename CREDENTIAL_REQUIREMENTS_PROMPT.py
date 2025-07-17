CREDENTIAL_REQUIREMENTS_PROMPT = '''You are provided an entire RfP document as text.
Therer may be multiple lots present. Each lot is to be separately applied for by the
company/organisation. So from the RfP document the following information needs to be extracted for each lot.
 
    1. Project value, if mentioned
    2. Scope of Services (be as elaborate as possible and has to include the overall scope of the work to be done)
    3. Country of work
    4. Domain
    5. Sector. Mention the main sector as well as umbrella sectors/domains that the skills come under.
     
    There needs to be another label called "Tags". The following information needs to be extracted as tags.
    6. Tags: [Category, Domain, Geographic Region, Project duration, Contract value, Credential age validity]
      In this,
    1. Category: Categorize the project into one of the following categories based on the content present in the RfP:
                a. Technology Consulting
                b. SaT (Strategy and Transactions)
                c. Tax
                d. Assurance
    2. Domain: Mention the domain of job that the project is most suitable for. This should be a broad-level title and
    should reflect the higher-level job domain (umbrella domain), rather than a specific field or job. This will be based
    on the entire content present in the RfP.
     
    Guidelines for 'Domain' extraction:
            - Focus on the broader category that encompasses the candidate's skills and experience.
            - Avoid using specific job titles; instead, use general terms that describe the field or area of expertise.
            - Consider the overall function and responsibilities associated with the candidate's experience.
        Example:
            - Specific job title: "Apex Developer"
            - Domain: "Front End Developer".
     
    3. Geographic Region: mention the geographic domain under which this RfP will require the team to work the project under.
    If the RfP mentions explicitly what region the credential should be covering, mention that.
    4. Project duration: mention the overall time required to complete the project as outlined in the RfP.
    If the RfP mentions explicitly the minimum or maximum duration of the project to be shown in the credential
    that should be mentioned.
    5. Contract value: mention the minimum contract value that the credential should have, if outlined in the
    RfP.
    6. Credential age validity: mention the maximum age of the credential that will be allowed as per the RfP.
    For example, sometimes they mention that credentials older than 3 years won't be allowed. In that scenario,
    3 years should be the output here.
 
    7. Requirements: This label should extract all the requirements that the credential should have.
    A credential requirement is denoted in the RFP documents as what the person who prepared the RFP is looking for from the company who would pick up the bid. These requirements are typically attached in the final response document by the bidding company.
    The credential requirements would generally be specific project criteria based on the past or previous project experiences of the bidding company that would eventually be selected to pick up the contract. This could include case studies or other professional ventures conducted by the bidding company in the past.
    The credential requirements are asked by the preparer of the RFP essentially to evaluate whether the bidding company is capable of picking up this bid. Hence, they are looking for information on past experience with similar projects.
    In the RFP documents, credential requirements could be denoted as a mandate or request to share previous client references, previous project value or revenue, previous project scope of services, previous project duration (typically with start and end dates), and/or an affirmation of similar projects being conducted by the bidding company in the past any number of years (generally 3 to 5).
    In some RFP documents, these credential requirements can be typically (but not always) found under sections like "requested evidence", "selection criteria", "references" (of past work/clients), or "past/previous experience". Use your discretion and only return requirements pertaining to past or previous PROJECTS, not personnel.
    Please extract only the credential requirements pertaining to the PROJECTS. Avoid mentioning ALL requirements pertaining to candidates, manpower, personnel, consultants, staff, teams of people of various designations, company or people profile, company or people turnover, and company or people finances. The final output strictly should not mention any of these. If there are any requirements alluding to the bidding company have to provide any of these, LEAVE these requirements OUT OF THE FINAL OUTPUT.
    The requirements should pertain to requirements like project value, credential age validity, number of credentials to attach, scope of services and location.
    As a Bid Manager, you should prepare the Credential Requirements ONLY FOR past or previous PROJECTS and not mention anything about the kind of people who were working in it. Do not extract anything about the ability of the bidding company to provide a certain kind of personnel. Focus only on the project details.
    Do not return conditions/requirement set for candidates.
    Do not return any generic content. It should be specific to the credentials to be attached. This content will help assess what kind of credentials can be attached in subsequent steps.
    The output should be a list of dictionaries, where each dictionary will contain information about each individual requirement.
    Furthermore, for each requirement, I need a "Status" field, which will be "Not approved" by default.
    Sample output for this key (should be specific to the RFP, this is only to give you an idea of the structure):
    "Requirements" : [dict("req": 1, "requirementDetail": "The evaluation will include a maximum of five specific country case studies.", "status": "Not approved"), dict("req": 2, "requirementDetail": "The evaluation should benchmark and identify lessons from similar initiatives.", "status": "Not approved"), dict("req": 3, "requirementDetail": "All credentials submitted must be no older than 3 years.", "status": "Not approved"), etc.]
    IMPORTANT NOTE: AVOID extracting anything mentioning the teams, designations or work experience of the people required of the bidding company. We want zero mentions of anything about people. We are focused only on the project details, not the people involved. Strictly avoid extracting content mentioning the designations or profiles of people required.
 
    For 10. Tags, only output the final list values, without the labels.
 
    The output needs to be in JSON format with these key value pairs. If any value for a key
    is not present, return "N/A".
 
    If multiple lots are present, the keys should be like Lot 1, Lot 2, etc. If only one lot is present, Lot 1 should be mentioned.
    The final output should be a dictionary/json like:
    dict(Lot 1: dictionary/json of the required keys listed above for Lot 1,
    Lot 2: dictionary/json of the required keys listed above for Lot 2)
 
    Note:
    - The keys need to be stored in camelCase format. For example, instead of "Project name", it should be "projectName".
    Another example is "Lot 1" becomes "lot1". This convention should be followed for all the keys in the output. This should be true for all keys of any dictionary,
    even if it is a nested dictionary. Make sure to follow this convention.
    '''