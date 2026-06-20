import { create } from "zustand";

export const useMetricsStore = create((set, get) => ({
  aiIssues: [],
  aiLoading: false,
  activeTab: "review",
  selectedFixIssueId: null,
  fixLoading: false,
  fixResult: null,

  // Setters
  setAiIssues: (aiIssues) => set({ aiIssues }),
  setAiLoading: (aiLoading) => set({ aiLoading }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setSelectedFixIssueId: (selectedFixIssueId) => set({ selectedFixIssueId }),
  setFixLoading: (fixLoading) => set({ fixLoading }),
  setFixResult: (fixResult) => set({ fixResult }),

  // Actions
  runCodeReview: async (codeContent, language) => {
    if (!codeContent) return;
    set({ aiLoading: true });
    try {
      const res = await fetch("/api/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeContent, language }),
      });
      const data = await res.json();
      if (data.errors) {
        set({ aiIssues: data.errors });
      }
    } catch (err) {
      console.error("Code review failed:", err);
    } finally {
      set({ aiLoading: false });
    }
  },
}));
