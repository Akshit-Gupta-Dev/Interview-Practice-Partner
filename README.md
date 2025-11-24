# Interview-Practice-Partner
Interactive interview simulation app with LLM and voice integration
*BRIEF DESCRIPTION*
An interactive application designed to simulate professional interviews across multiple roles and domains. The system provides a structured environment where candidates can practice answering questions, receive feedback, and experience realistic interviewer personas. It integrates a graphical interface, large language model orchestration, and optional voice input/output for a complete practice experience.

Requirements
- Python 3.9 or higher
- Tkinter and ttk (standard with Python)
- SpeechRecognition and pyttsx3 for voice input/output
- Ollama installed locally with access to the Mistral model
- JSON configuration files for roles, rubrics, and prompts

Setup Instructions
- Clone the repository into your local environment.
- Install the required Python dependencies using the provided requirements list.
- Ensure Ollama is installed and the Mistral model is available locally.
- Verify that the data directory contains the necessary configuration files (roles.json, rubric.json, and prompt templates).
- Launch the application by running the main GUI script.

Architecture Notes
- Graphical Interface (GUI): Built with Tkinter, providing dropdowns for role, seniority, domain, and persona selection. Includes a styled chat box for interviewer and candidate interactions, as well as controls for sending or recording answers.
- LLM Client: A lightweight wrapper around Ollama, responsible for executing prompts and returning generated text.
- Orchestrator: Manages interview state transitions, loads role definitions and rubrics, and generates questions, follow-ups, feedback, and summaries.
- Voice Controller: Handles optional speech-to-text and text-to-speech functionality, enabling spoken interaction with the interviewer.
- Data Files: Externalized JSON and text templates define roles, rubrics, and prompt structures, ensuring flexibility and easy updates.

Design Decisions
- Separation of Concerns: Each component (GUI, orchestrator, LLM client, voice utilities) is modular, allowing independent updates and maintenance.
- Extensibility: New roles, domains, and personas can be added by updating configuration files without modifying core logic.
- Error Handling: Critical operations are wrapped with exception handling, ensuring user-friendly error messages and graceful recovery.
- Structured Feedback: A rubric-driven evaluation ensures consistent scoring across clarity, technical depth, relevance, and confidence.
- User Experience: The interface is styled for readability and professionalism, with clear differentiation between interviewer, candidate, feedback, and summary messages.
- Demo Readiness: Defaults are set for role, domain, and persona to allow quick demonstration without extensive setup.

Future Enhancements
- Non-blocking voice and feedback generation using threading for improved responsiveness.
- Persistent session transcripts for later review.
- Expanded role library and customizable rubrics for broader applicability.
- Integration with cloud-based LLMs for enhanced scalability and model variety.
