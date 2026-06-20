import { create } from "zustand";

export const useAgentStore = create((set, get) => ({
  agentPrompt: "",
  agentFilename: "automation_agent.py",
  agentRunning: false,
  agentVisibleLogs: [],
  agentResult: null,
  isListening: false,
  assistantMessages: [
    { sender: "assistant", text: "Welcome to APCRE 4.0 Ecosystem! I am your Autonomous Engineering Coordinator. Ask me anything about class structures, security issues, or AST optimizations." }
  ],
  assistantInput: "",
  assistantLoading: false,

  // Setters
  setAgentPrompt: (agentPrompt) => set({ agentPrompt }),
  setAgentFilename: (agentFilename) => set({ agentFilename }),
  setAgentRunning: (agentRunning) => set({ agentRunning }),
  setAgentVisibleLogs: (agentVisibleLogs) => set({ agentVisibleLogs }),
  setAgentResult: (agentResult) => set({ agentResult }),
  setIsListening: (isListening) => set({ isListening }),
  setAssistantMessages: (assistantMessages) => set({ assistantMessages }),
  setAssistantInput: (assistantInput) => set({ assistantInput }),
  setAssistantLoading: (assistantLoading) => set({ assistantLoading }),

  // Actions
  addAssistantMessage: (msg) => {
    set((state) => ({
      assistantMessages: [...state.assistantMessages, msg]
    }));
  },

  sendAssistantMessage: async (text) => {
    if (!text.trim()) return;
    const userMsg = { sender: "user", text };
    get().addAssistantMessage(userMsg);
    set({ assistantInput: "", assistantLoading: true });

    try {
      const res = await fetch("/api/assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      if (data.reply) {
        get().addAssistantMessage({ sender: "assistant", text: data.reply });
      }
    } catch (err) {
      get().addAssistantMessage({ sender: "assistant", text: "⚠️ Error contacting APCRE Agent backend service." });
    } finally {
      set({ assistantLoading: false });
    }
  }
}));
