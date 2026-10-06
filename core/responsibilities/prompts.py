from core.responsibilities.project import Project

class ProjectStatusPrompt:
    @staticmethod
    def generate(project: Project) -> str:
        state = project.get_structured_state()
        
        prompt = f"Summarize project state for: {state['project_name']}\n\n"
        prompt += f"Status: {state['status']}\n\n"
        prompt += "Include:\n"
        prompt += "- current goals\n- completed milestones\n- active tasks\n- blocked tasks\n- failures\n- upcoming deadlines\n- user decisions required\n\n"
        prompt += "Do not infer completion from lack of recent errors.\nUse explicit task state and evidence.\n\n"
        
        prompt += "### Project Structure Data:\n"
        for r in state["responsibilities"]:
            prompt += f"Responsibility: {r['name']} [{r['status']}]\n"
            for g in r["goals"]:
                prompt += f"  Goal: {g['name']} [{g['status']}]\n"
                for t in g["tasks"]:
                    prompt += f"    Task: {t['name']} [{t['status']}]\n"
        
        return prompt
