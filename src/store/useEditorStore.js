import { create } from "zustand";

export const useEditorStore = create((set, get) => ({
  files: [],
  selectedFile: null,
  filesLoading: false,
  workspacePath: "",
  showOpenFolderModal: false,
  openFolderPathInput: "c:\\Users\\WAZIR AMMAR HAIDER\\Desktop\\fyp\\Source_Code",
  toastMessage: "",

  // Setters
  setFiles: (files) => set({ files }),
  setSelectedFile: (selectedFile) => set({ selectedFile }),
  setFilesLoading: (filesLoading) => set({ filesLoading }),
  setWorkspacePath: (workspacePath) => set({ workspacePath }),
  setShowOpenFolderModal: (showOpenFolderModal) => set({ showOpenFolderModal }),
  setOpenFolderPathInput: (openFolderPathInput) => set({ openFolderPathInput }),
  setToastMessage: (toastMessage) => {
    set({ toastMessage });
    if (toastMessage) {
      setTimeout(() => {
        if (get().toastMessage === toastMessage) {
          set({ toastMessage: "" });
        }
      }, 1500);
    }
  },

  // Actions
  loadFilesFromBackend: async (customPath = "") => {
    const pathStr = customPath || get().workspacePath;
    if (!pathStr) return;
    set({ filesLoading: true });
    try {
      const res = await fetch(`/api/files?path=${encodeURIComponent(pathStr)}`);
      const data = await res.json();
      if (Array.isArray(data)) {
        set({ files: data });
        // Restore selected file state
        const currentSelected = get().selectedFile;
        if (currentSelected) {
          const updated = data.find((f) => f.path === currentSelected.path);
          if (updated) set({ selectedFile: updated });
        }
      }
    } catch (err) {
      console.error("Failed to load files:", err);
    } finally {
      set({ filesLoading: false });
    }
  },
}));
