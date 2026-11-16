"""Optional CrewAI hierarchical-delegation demo. Run after installing CrewAI and configuring its LLM provider."""
try:
    from crewai import Agent, Task, Crew, Process
except ImportError as exc:
    raise SystemExit("Install optional dependencies: pip install '.[dev]'") from exc

researcher=Agent(role="Knowledge Researcher",goal="Find relevant evidence and report source-backed findings",backstory="Careful enterprise knowledge analyst",verbose=True)
analyst=Agent(role="Operations Analyst",goal="Turn evidence into a concise operational recommendation",backstory="Quantitative operations specialist",verbose=True)
reviewer=Agent(role="Quality Reviewer",goal="Check factual support, omissions, and unsafe assumptions",backstory="Sceptical reviewer",verbose=True)
research=Task(description="Research this request using only supplied context: {request}",expected_output="Evidence summary with explicit unknowns",agent=researcher)
analysis=Task(description="Analyse the research findings and produce a recommendation",expected_output="Recommendation with rationale",agent=analyst,context=[research])
review=Task(description="Review the recommendation for unsupported claims and risks",expected_output="Approved or corrected final answer",agent=reviewer,context=[research,analysis])
crew=Crew(agents=[researcher,analyst,reviewer],tasks=[research,analysis,review],process=Process.hierarchical,verbose=True)
if __name__=="__main__": print(crew.kickoff(inputs={"request":"Summarise risks in a sample customer onboarding process."}))
