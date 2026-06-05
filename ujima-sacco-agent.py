import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process

# -------------------------------------------------------------------------
# SETUP & CONFIGURATION
# -------------------------------------------------------------------------
# Ensuring execution environment configurations match local telemetry rules.
# Production configurations target AWS Africa endpoints via local proxies.
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"  # Target local inference for data sovereignty
os.environ["OPENAI_MODEL_NAME"] = "llama3"                  # Local deployment model
os.environ["OPENAI_API_KEY"] = "local-sovereignty-key"

# -------------------------------------------------------------------------
# AGENT ARCHITECTURES (RANK Calibrated)
# -------------------------------------------------------------------------

scout_agent = Agent(
    role="Scout Agent (Financial Literacy Coach)",
    goal="Educate members on harvest-cycle planning and identify financial stress signals safely.",
    backstory=(
        "You are an empathetic financial coach rooted in East African economic realities. "
        "You understand matooke and maize harvest fluctuations. You talk like a supportive, wise auntie. "
        "RANK Rules: Max 3 SMS statements per day. Never recommend specific loan products directly. "
        "If a member mentions predatory terms or severe stress ('loan shark', 'no money for school fees'), "
        "you immediately flag the conversation for triage."
    ),
    allow_delegation=False,
    verbose=True
)

guardian_agent = Agent(
    role="Guardian Agent (Loan Triage Evaluator)",
    goal="Perform initial Tier-1 credit screening against strict agricultural liquidity timelines.",
    backstory=(
        "You are an analytical credit risk assessor. You review financial inputs against SASRA and "
        "Kenya DPA 2022 standards. RANK Rules: You can only auto-approve lines <= KES 15,000. "
        "You must trigger an immediate escalation to human handling via the Hunter Agent if the application "
        "exceeds KES 15,000, if the member has 2+ children under 5, or if high-stress flags exist. "
        "You maintain a very low temperature setting to avoid mathematical errors or fabrications."
    ),
    allow_delegation=False,
    verbose=True
)

hunter_agent = Agent(
    role="Hunter Agent (Human-in-the-Loop Coordinator)",
    goal="Coordinate human loan officers, compile deep analytical dossiers, and ensure human accountability.",
    backstory=(
        "You are the operational coordinator. RANK Rules: You NEVER issue an automated final approval or denial "
        "decision for escalated cases. Your sole function is to assemble comprehensive, highly contextualized briefing "
        "packets for licensed human credit officers, matching applications to the officer's specific crop/market expertise."
    ),
    allow_delegation=False,
    verbose=True
)

# -------------------------------------------------------------------------
# MOCK INPUT TRANSACTION DATA DATASTATE
# -------------------------------------------------------------------------
mock_member_session = {
    "applicant_name": "Grace Wambui",
    "occupation": "Market Vendor (Maize/Beans)",
    "location": "Kakamega Sub-county",
    "dependents_count": 3,
    "ages_of_children": [4, 7, 11],
    "raw_sms_input": "Sina pesa ya kulipa karo ya shule mwezi huu (I have no money for school fees this month), help me.",
    "requested_amount_kes": 28000,
    "historical_savings_kes": 4500,
    "projected_harvest_peak": "October/November"
}

# -------------------------------------------------------------------------
# TASK ARCHITECTURES & HANDOFF TRIGGERS
# -------------------------------------------------------------------------

scout_literacy_task = Task(
    description=(
        f"Analyze the inbound user communication: '{mock_member_session['raw_sms_input']}'. "
        "Formulate a supportive, 3-sentence response in clear Sheng/Swahili advising on cash-flow management "
        "without promising money. Check for high-stress indicators. "
        "If a stress indicator is confirmed, output a structured alert package containing: "
        f"[Context: {mock_member_session['applicant_name']}, Requesting: KES {mock_member_session['requested_amount_kes']}]."
    ),
    expected_output="A 3-sentence empathetic literacy text AND a structured handoff payload if stress is identified.",
    agent=scout_agent
)

guardian_triage_task = Task(
    description=(
        "Evaluate the credit eligibility profile compiled from the database state: "
        f"Occupation: {mock_member_session['occupation']}. Request Amount: KES {mock_member_session['requested_amount_kes']}. "
        f"Dependents: {mock_member_session['dependents_count']} children (Ages: {mock_member_session['ages_of_children']}). "
        "Evaluate compliance with strict parameters: Is amount > KES 15,000? Are there children under 5 present? "
        "If yes to either condition, execute an immediate handoff to the Hunter Agent with an analytical summary of seasonal income variances."
    ),
    expected_output="An explicit triage status evaluation report detailing whether the criteria trigger a mandatory human routing.",
    agent=guardian_agent
)

hunter_coordination_task = Task(
    description=(
        "Consolidate the operational intelligence generated by the preceding tasks. "
        f"Compile a structured Briefing Packet for credit officer assignment. "
        f"Match Grace Wambui's profile to an available agricultural loan advisor specializing in Kakamega region dynamics. "
        "The briefing packet must include: Applicant details, seasonal income peak analysis, "
        "risk mitigation indicators (e.g., cross-selling crop insurance), and an explicit PRIDE Loop validation link."
    ),
    expected_output="A formal, comprehensive human-officer dossier with clear structural recommendations and no automated denials.",
    agent=hunter_agent
)

# -------------------------------------------------------------------------
# ORCHESTRATION INGESTION
# -------------------------------------------------------------------------
ujima_pride_crew = Crew(
    agents=[scout_agent, guardian_agent, hunter_agent],
    tasks=[scout_literacy_task, guardian_triage_task, hunter_coordination_task],
    process=Process.sequential,  # Enforces systemic step-by-step pipeline progression
    verbose=True
)

if __name__ == "__main__":
    print(f"--- INITIALIZING UJIMA AGENT PRIDE ECOSYSTEM RUNTIME: {datetime.now().isoformat()} ---")
    runtime_result = ujima_pride_crew.kickoff()
    print("\n--- FINAL OUTPUT DOSSIER FOR HUMAN-IN-THE-LOOP ENTRY ---")
    print(runtime_result)