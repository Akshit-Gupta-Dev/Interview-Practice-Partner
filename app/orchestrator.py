import json
from pathlib import Path

class InterviewState:
    INIT = "init"
    QUESTION = "question"
    FOLLOWUP = "followup"
    FEEDBACK = "feedback"
    SUMMARY = "summary"
    END = "end"

class Orchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.state = InterviewState.INIT
        self.ctx = {
            "role": None,
            "seniority": None,
            "domain": None,
            "persona": "efficient",
            "answers": [],
            "feedback": []
        }
        # Load configs
        self.roles = json.loads(Path("data/roles.json").read_text())
        self.rubric = json.loads(Path("data/rubric.json").read_text())
        self.prompts = {
            "interviewer": Path("data/prompts/interviewer.txt").read_text(),
            "followup": Path("data/prompts/followup.txt").read_text(),
            "feedback": Path("data/prompts/feedback.txt").read_text(),
            "summary": Path("data/prompts/summary.txt").read_text(),
        }

    def set_profile(self, role, seniority, domain, persona):
        # Normalize Title Case values from GUI to lowercase keys
        role = role.lower().replace(" ", "_")
        seniority = seniority.lower()
        domain = domain.lower()
        persona = persona.lower()

        # Validate domain against role
        role_pack = self.roles["roles"].get(role)
        if role_pack and domain not in role_pack["domains"]:
            # fallback to first domain if invalid
            domain = role_pack["domains"][0]

        self.ctx.update({
            "role": role,
            "seniority": seniority,
            "domain": domain,
            "persona": persona
        })
        self.state = InterviewState.QUESTION

    def _format(self, template, **kwargs):
        return template.format(**kwargs)

    def next_question(self):
        role_pack = self.roles["roles"][self.ctx["role"]]
        axes = ", ".join(role_pack["technical_axes"])
        persona_style = self.roles["personas"][self.ctx["persona"]]["style"]
        seeds = "; ".join(role_pack["question_seeds"])

        prompt = self._format(
            self.prompts["interviewer"],
            role=self.ctx["role"],
            seniority=self.ctx["seniority"],
            domain=self.ctx["domain"],
            persona_style=persona_style,
            technical_axes=axes,
            question_seeds=seeds
        )
        self.state = InterviewState.FOLLOWUP
        return self.llm.generate(prompt)

    def followup(self, last_answer: str):
        persona_style = self.roles["personas"][self.ctx["persona"]]["style"]
        prompt = self._format(
            self.prompts["followup"],
            answer=last_answer,
            persona_style=persona_style
        )
        self.state = InterviewState.FEEDBACK
        self.ctx["answers"].append(last_answer)
        return self.llm.generate(prompt)

    def feedback(self, last_answer: str):
        prompt = self._format(
            self.prompts["feedback"],
            answer=last_answer,
            role=self.ctx["role"],
            seniority=self.ctx["seniority"],
            domain=self.ctx["domain"],
            persona=self.ctx["persona"]
        )
        raw = self.llm.generate(prompt)
        try:
            j = json.loads(raw)
        except Exception:
            j = {"scores": {}, "strengths": [], "improvements": [], "raw": raw}

        # Apply rubric guidance if missing
        if not j.get("strengths"):
            j["strengths"] = self.rubric["guidance"]["strength_starters"]
        if not j.get("improvements"):
            j["improvements"] = self.rubric["guidance"]["improvement_starters"]

        self.ctx["feedback"].append(j)
        self.state = InterviewState.QUESTION
        return j

    def summary(self):
        prompt = self._format(
            self.prompts["summary"],
            role=self.ctx["role"],
            seniority=self.ctx["seniority"],
            domain=self.ctx["domain"]
        )
        self.state = InterviewState.END
        return self.llm.generate(prompt)