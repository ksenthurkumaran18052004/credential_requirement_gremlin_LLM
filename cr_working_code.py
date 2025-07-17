import json
import asyncio
from gremlin_python.driver import client, serializer
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from CREDENTIAL_REQUIREMENTS_PROMPT import CREDENTIAL_REQUIREMENTS_PROMPT

# === PATCH for Windows asyncio bug ===
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === STEP 1: Gremlin Client Setup ===
gremlin_client = client.Client(
    'wss://euwdpsi14hcdb02.gremlin.cosmos.azure.com:443/',
    'g',
    username="/dbs/CredentialsDB/colls/CredGraphV2",
    password="key",
    message_serializer=serializer.GraphSONSerializersV2d0()
)

# === STEP 2: Gremlin Query Sender ===
def send_gremlin(query):
    try:
        return gremlin_client.submit(query).all().result()
    except Exception as e:
        if "Conflict" in str(e) or "already exists" in str(e):
            return "DUPLICATE"
        print("❌ Gremlin Error:", e)
        return []

def safe_str(val):
    if isinstance(val, list):
        return ", ".join(str(x) for x in val)
    if val is None:
        return "N/A"
    return str(val)

# === STEP 3: Insert Credentials from JSON ===
def insert_credentials_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for idx, cred in enumerate(data):
            cred_data = cred.get("credentialData", {})
            id_val = safe_str(cred.get("id", str(idx)))
            project_name = safe_str(cred_data.get('projectName', 'N/A')).replace("'", "\\'")
            client_name = safe_str(cred_data.get('clientName', 'N/A')).replace("'", "\\'")
            domain = safe_str(cred.get("tags", {}).get('domain', 'General')).replace("'", "\\'")
            file_name = safe_str(cred.get("fileName", 'N/A')).replace("'", "\\'")
            region = safe_str(cred.get("tags", {}).get('geographicRegion', 'Global')).replace("'", "\\'")
            tools_used = safe_str(cred.get("scopeOfServices", {}).get('toolsTechnologies', '')).replace("'", "\\'")
            description = safe_str(cred_data.get("detailedDescription", 'N/A')).replace("'", "\\'")
            category = safe_str(cred.get("tags", {}).get('category', "Credential"))

            query = f"""
                g.addV('Credential')
                 .property('id', '{id_val}')
                 .property('projectName', '{project_name}')
                 .property('clientName', '{client_name}')
                 .property('domain', '{domain}')
                 .property('category', '{category}')
                 .property('pk', '{category}')
                 .property('fileName', '{file_name}')
                 .property('region', '{region}')
                 .property('toolsUsed', '{tools_used}')
                 .property('description', '{description}')
            """
            result = send_gremlin(query)

            if result == "DUPLICATE":
                print(f"⚠️ Already exists credential #{idx+1}: {project_name}")
            elif result:
                print(f"✅ Inserted credential #{idx+1}: {project_name}")
            else:
                print(f"❌ Failed to insert credential #{idx+1}: {project_name}")

    except Exception as e:
        print("❌ Insertion error:", e)



# === STEP 4: Retrieve All Credentials ===
def retrieve_all_credentials():
    query = "g.V().hasLabel('Credential').valueMap(true)"
    return send_gremlin(query)

# === STEP 5: LLM Call – Extract Requirements from JD Text ===
def extract_requirements_from_jd(jd_text):
    # llm = AzureChatOpenAI(
    #     api_key="key",  # 🔐 Replace with your Azure OpenAI key
    #     azure_endpoint="https://usedoai4xnaoa01.openai.azure.com/",
    #     api_version="2024-12-01-preview",
    #     azure_deployment="gpt-4o-mini",
    #     temperature=0.1
    # )

    messages = [
        SystemMessage(content="You are an expert Bid Manager."),
        HumanMessage(content=CREDENTIAL_REQUIREMENTS_PROMPT + "\n\n" + jd_text)
    ]

    response = llm.invoke(messages)
    return response.content


def match_credentials_to_requirements(credentials, extracted_lot):
    scope_text = extracted_lot.get("scopeOfServices", "").lower()
    sectors = [s.lower() for s in extracted_lot.get("sector", {}).get("umbrellaSectors", [])]
    
    matches = {}

    for cred in credentials:
        cred_id = cred.get("id", ["N/A"])[0]
        project_name = cred.get("projectName", ["N/A"])[0]
        description = cred.get("description", [""])[0].lower()
        tools_used = cred.get("toolsUsed", [""])[0].lower()
        domain = cred.get("domain", [""])[0].lower()
        region = cred.get("region", [""])[0].lower()
        
        match_score = 0
        keywords = scope_text + " " + " ".join(sectors)

        for term in keywords.split():
            if term in description or term in tools_used or term in domain or term in region:
                match_score += 1

        if match_score > 0:
            matches[cred_id] = {
                "projectName": project_name,
                "matchScore": match_score,
                "descriptionSnippet": description[:250]
            }

    return matches

# === STEP 6: Main Execution ===
if __name__ == "__main__":
    print("\n🟡 Inserting credentials into Gremlin...\n")
    insert_credentials_from_json("credPoolData.json")

    print("\n🟡 Retrieving from Gremlin...\n")
    all_credentials = retrieve_all_credentials()

    print("\n🟡 Please paste the JD or RFP text below (end with ENTER + CTRL+Z on Windows or ENTER + CTRL+D on Mac/Linux):\n")
    jd_input = ""
    try:
        while True:
            line = input()
            jd_input += line + "\n"
    except EOFError:
        pass

    print("\n🟡 Sending JD to LLM...\n")
    result = extract_requirements_from_jd(jd_input)

    # === Clean markdown code blocks ===
    cleaned_result = result.strip()
    if cleaned_result.startswith("```json"):
        cleaned_result = cleaned_result[7:-3].strip()
    elif cleaned_result.startswith("```"):
        cleaned_result = cleaned_result[3:-3].strip()

    try:
        requirement_json = json.loads(cleaned_result)
    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("🔎 Raw LLM output was:\n", result)
        exit(1)

    # === Save output JSON ===
    with open("requirement_output.json", "w", encoding="utf-8") as f:
        json.dump(requirement_json, f, indent=2)
    print("\n🟢 Saved structured requirements to requirement_output.json")

    lot1_data = requirement_json.get("lot1", {})
    matches = match_credentials_to_requirements(all_credentials, lot1_data)

    print("\n🎯 Matching Credentials:\n")
    for cid, info in matches.items():
        print(f"- ID: {cid}")
        print(f"  Name: {info['projectName']}")
        print(f"  Score: {info['matchScore']}")
        print(f"  Desc: {info['descriptionSnippet']}\n")

    print("✅ Done.")