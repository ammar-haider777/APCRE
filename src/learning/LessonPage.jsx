import React, { useState, useEffect, useRef } from "react";
import Editor, { useMonaco } from "@monaco-editor/react";

export default function LessonPage({ lesson, onBack, onComplete, hasNextLesson, onNextLesson }) {
  const [code, setCode] = useState("");
  const [started, setStarted] = useState(false);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitStatus, setSubmitStatus] = useState("submit"); // "submit" | "submitted"
  const [showVideoModal, setShowVideoModal] = useState(false);

  // == COLLABORATIVE DISCUSSION STATES & HANDLERS ==
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState("");
  const [likedMsgIds, setLikedMsgIds] = useState([]);
  const [replyingTo, setReplyingTo] = useState(null);
  const [activeCount, setActiveCount] = useState(1);
  const [timeTicker, setTimeTicker] = useState(0);

  // Poll active users count from the backend
  useEffect(() => {
    const fetchActiveUsers = async () => {
      try {
        const res = await fetch("/api/active-users");
        const data = await res.json();
        if (data.activeCount) {
          setActiveCount(data.activeCount);
        }
      } catch (err) {
        setActiveCount(1);
      }
    };

    fetchActiveUsers();
    const interval = setInterval(fetchActiveUsers, 5000);
    return () => clearInterval(interval);
  }, []);

  // Force timestamp re-renders every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeTicker((t) => t + 1);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // 1. Get default mock messages for this lesson
    const defaultMocks = {
      1: [ // Variables & Print
        { id: "m1", name: "Mudassar", avatar: "MU", text: "Remember that Python variables are case-sensitive! 'x' is completely different from 'X'!", likes: 5, time: "2 hours ago" },
        { id: "m2", name: "Mariyam", avatar: "MA", text: "Does the print function name need to be lowercase?", likes: 3, time: "1 hour ago" },
        { id: "m3", name: "Muneer", avatar: "MR", text: "Yes, 'print()' must be all lowercase. If you write 'Print()', Python will throw a NameError!", likes: 8, time: "45 mins ago" }
      ],
      2: [ // Arithmetic Operators
        { id: "m1", name: "Ammar", avatar: "AM", text: "Standard math operator rules apply. Multiplication '*' has higher precedence than addition '+'!", likes: 6, time: "3 hours ago" },
        { id: "m2", name: "Mariyam", avatar: "MA", text: "We can perform operations directly inside the print statement: print(7 * 8).", likes: 10, time: "1 hour ago" }
      ],
      3: [ // String Manipulation
        { id: "m1", name: "Muneer", avatar: "MR", text: "Make sure you include a space string ' ' in the middle, otherwise the words will be stuck together!", likes: 9, time: "5 hours ago" },
        { id: "m2", name: "Mudassar", avatar: "MU", text: "You can concatenate strings using the '+' symbol. Like \"Hello\" + \" \" + \"World\".", likes: 4, time: "2 hours ago" }
      ],
      4: [ // Lists & Indexing
        { id: "m1", name: "Mariyam", avatar: "MA", text: "Index counting starts at 0! So the 1st item is [0], and the 2nd item is at index [1]!", likes: 15, time: "1 day ago" },
        { id: "m2", name: "Ammar", avatar: "AM", text: "Yes! Creating colors = ['red', 'green', 'blue'] and printing colors[1] will print 'green'.", likes: 7, time: "3 hours ago" }
      ],
      5: [ // Conditionals (If-Else)
        { id: "m1", name: "Muneer", avatar: "MR", text: "Don't forget the colon ':' at the end of the 'if' and 'else' lines! It will cause a SyntaxError if omitted.", likes: 14, time: "8 hours ago" },
        { id: "m2", name: "Mudassar", avatar: "MU", text: "Also check your indentation! Indent the print statements inside the if and else blocks by 4 spaces.", likes: 11, time: "4 hours ago" }
      ],
      6: [ // For Loops
        { id: "m1", name: "Mariyam", avatar: "MA", text: "Make sure you convert the integer 'n' to a string using str(n) when concatenating it with 'item '!", likes: 8, time: "10 hours ago" },
        { id: "m2", name: "Ammar", avatar: "AM", text: "Yes! Python doesn't allow direct concatenation of strings and integers without type conversion.", likes: 6, time: "2 hours ago" }
      ],
      7: [ // Functions
        { id: "m1", name: "Muneer", avatar: "MR", text: "Define the function using 'def greet(name):' and don't forget to call it afterwards passing 'Ammar'!", likes: 12, time: "12 hours ago" }
      ],
      8: [ // Dictionaries
        { id: "m1", name: "Mudassar", avatar: "MU", text: "Use square brackets to access keys: print(user_profile['username']).", likes: 9, time: "1 day ago" }
      ]
    };

    const lessonId = lesson.id;
    const storageKey = `apcre_discussion_lesson_${lessonId}`;
    const stored = localStorage.getItem(storageKey);

    const storedLikes = localStorage.getItem(`apcre_discussion_likes_${lessonId}`);
    setLikedMsgIds(storedLikes ? JSON.parse(storedLikes) : []);
    setReplyingTo(null);

    if (stored) {
      setMessages(JSON.parse(stored));
    } else {
      const initial = defaultMocks[lessonId] || [
        { id: "m1", name: "Peer Learner", avatar: "PL", text: "Welcome to this chapter discussion board! Let's help each other out.", likes: 2, time: "Just now" }
      ];
      setMessages(initial);
      localStorage.setItem(storageKey, JSON.stringify(initial));
    }
  }, [lesson.id]);

  const getLoggedInUserInfo = () => {
    const storedUser = localStorage.getItem("user");
    let currentName = "Ammar Haider";
    let currentAvatar = "AH";
    
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        if (parsed.name) {
          currentName = parsed.name;
        } else if (parsed.username) {
          currentName = parsed.username;
        }
        if (currentName) {
          const parts = currentName.split(" ");
          currentAvatar = parts.map(p => p[0]).join("").substring(0, 2).toUpperCase();
        }
      } catch (e) {}
    }
    return { name: currentName, avatar: currentAvatar };
  };

  const getRelativeTime = (msg) => {
    if (!msg.timestamp) {
      return msg.time || "Just now";
    }
    const diffMs = Date.now() - msg.timestamp;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) {
      return "Just now";
    } else if (diffMins < 60) {
      return `${diffMins} ${diffMins === 1 ? "min" : "mins"} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`;
    } else {
      return `${diffDays} ${diffDays === 1 ? "day" : "days"} ago`;
    }
  };

  const handleSendMessage = () => {
    const text = newMsg.trim();
    if (!text) return;

    const userInfo = getLoggedInUserInfo();

    const newMessageObj = {
      id: Date.now().toString(),
      name: userInfo.name,
      avatar: userInfo.avatar,
      text: text,
      likes: 0,
      timestamp: Date.now(),
      replyTo: replyingTo ? replyingTo.name : null
    };

    const updated = [...messages, newMessageObj];
    setMessages(updated);
    setNewMsg("");
    setReplyingTo(null);

    const storageKey = `apcre_discussion_lesson_${lesson.id}`;
    localStorage.setItem(storageKey, JSON.stringify(updated));
  };

  const handleLikeMessage = (msgId) => {
    // Prevent duplicate likes per person
    if (likedMsgIds.includes(msgId)) return;

    const updated = messages.map((m) => {
      if (m.id === msgId) {
        return { ...m, likes: m.likes + 1 };
      }
      return m;
    });
    setMessages(updated);
    const storageKey = `apcre_discussion_lesson_${lesson.id}`;
    localStorage.setItem(storageKey, JSON.stringify(updated));

    const updatedLikes = [...likedMsgIds, msgId];
    setLikedMsgIds(updatedLikes);
    localStorage.setItem(`apcre_discussion_likes_${lesson.id}`, JSON.stringify(updatedLikes));
  };

  const monaco = useMonaco();
  const editorRef = useRef(null);

  /* == REAL-TIME AI CODE REVIEW & AUTOCOMPLETE == */
  useEffect(() => {
    if (!monaco) return;

    // 1. Register AI Autocomplete Provider
    const completionProvider = monaco.languages.registerCompletionItemProvider("python", {
      provideCompletionItems: async (model, position) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column,
        });

        try {
          const res = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: textUntilPosition }),
          });
          const aiResponse = await res.json();
          
          // Assuming AI returns a 'suggestions' array matching what comes next
          const suggestions = (aiResponse.suggestions || []).map((sugg) => ({
            label: sugg.text,
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: sugg.text,
            detail: "AI Model Suggestion",
          }));

          return { suggestions };
        } catch (e) {
          return { suggestions: [] };
        }
      },
    });

    return () => {
      completionProvider.dispose();
    };
  }, [monaco]);

  useEffect(() => {
    if (!monaco || !editorRef.current || !code) return;
    
    // 2. Debounce typing to request AI Review for syntax/errors
    const timer = setTimeout(async () => {
      try {
        const res = await fetch("/api/review", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code })
        });
        const aiAnalysis = await res.json();
        
        // Map Flask AI errors to Monaco Editor syntax errors
        const markers = (aiAnalysis.errors || []).map(err => ({
          message: err.message,
          severity: monaco.MarkerSeverity.Error,
          startLineNumber: err.line,
          startColumn: err.column || 1,
          endLineNumber: err.line,
          endColumn: err.endColumn || 10,
        }));
        
        monaco.editor.setModelMarkers(editorRef.current.getModel(), "ai-reviewer", markers);
      } catch (err) {
        console.log("AI Model unreachable");
      }
    }, 1500);

    return () => clearTimeout(timer);
  }, [code, monaco]);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
  };

  if (!lesson) return null;

  /* ================= RUN CODE ================= */
  const runCode = async () => {
    setLoading(true);
    setOutput("Running...");

    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename: "lesson.py",
          code: code,
        }),
      });

      const data = await res.json();

      const finalOutput = data.stdout || data.stderr || "";
      setOutput(finalOutput);

      return finalOutput; // ✅ IMPORTANT
    } catch (err) {
      setOutput("❌ Backend not running");
      return "";
    } finally {
      setLoading(false);
    }
  };

  /* ================= RUN TERMINAL COMMAND ================= */
  const runTerminalCommand = async (cmd) => {
    setOutput((prev) => prev + `\n> ${cmd}\n`);

    try {
      const res = await fetch("/api/terminal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd }),
      });

      const data = await res.json();
      setOutput((prev) => prev + (data.output || "") + "\n");
    } catch (err) {
      setOutput((prev) => prev + `❌ ${err.message}\n`);
    }
  };

  /* ================= SUBMIT ================= */
  const submitCode = async () => {
    if (submitStatus === "submitted") return;
    const result = await runCode(); // ✅ use fresh result

    if (result.trim().includes(lesson.expectedOutput.trim())) {
      setSubmitStatus("submitted");
      setOutput(result + "\n\n✅ Correct Solution!");

      if (onComplete) {
        onComplete(); // ✅ progress update
      }
    } else {
      setSubmitStatus("submit");
      setOutput(result + "\n\n❌ Wrong Output. Try again!");
    }
  };

  return (
    <div className="flex h-[calc(100vh-56px)] bg-[#0B1220] text-slate-200">
      {/* LEFT SIDE */}
      <div className="w-1/2 p-8 overflow-auto border-r border-slate-800/80 space-y-6 scrollbar-thin">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold uppercase font-mono tracking-wider text-blue-400 hover:text-blue-300 transition"
        >
          <span>← Back to Courses</span>
        </button>

        {lesson.videoUrl && (
          <div className="mt-4 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950/40 shadow-lg select-none">
            <div className="relative pt-[56.25%]">
              <iframe
                className="absolute inset-0 w-full h-full border-none"
                src={lesson.videoUrl}
                title="Tutorial Video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        )}

        <h1 className="text-2xl font-bold text-white tracking-tight leading-tight">{lesson.title}</h1>

        {/* ================= INTRODUCTION ================= */}
        <div className="space-y-2">
          <h2 className="text-xs font-bold text-slate-400 font-mono uppercase tracking-wider">
            📘 Theory & Concept
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line font-semibold">
            {lesson.introduction}
          </p>
        </div>

        {/* ================= EXAMPLE CODE ================= */}
        {lesson.exampleCode && (
          <div className="space-y-2">
            <h2 className="text-xs font-bold text-slate-400 font-mono uppercase tracking-wider">
              💡 Code Blueprint
            </h2>
            <pre className="bg-[#070a13] border border-slate-850 text-emerald-400 p-4 rounded-xl text-xs overflow-x-auto font-mono">
              <code>{lesson.exampleCode}</code>
            </pre>
          </div>
        )}

        {/* ================= TASK ================= */}
        <div className="bg-blue-950/20 border border-blue-900/40 p-6 rounded-2xl mt-6 space-y-2 text-left">
          <h2 className="text-sm font-bold text-blue-400 font-mono uppercase tracking-wider">💻 Active Challenge</h2>
          <p className="text-xs text-blue-300 whitespace-pre-line leading-relaxed font-semibold">
            {lesson.task}
          </p>
        </div>

        {!started && (
          <button
            onClick={() => {
              setCode(lesson.starterCode);
              setStarted(true);
            }}
            className="mt-4 bg-blue-600 text-white font-extrabold uppercase font-mono tracking-wider text-xs px-6 py-3 rounded-xl hover:bg-blue-700 shadow-md hover:shadow-lg transition duration-300 w-full"
          >
            Start Challenge Editor
          </button>
        )}

        {/* ================= COLLABORATIVE DISCUSSION PANEL ================= */}
        <div className="border-t border-slate-800/80 pt-8 mt-8 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">💬</span>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Student Discussions</h2>
            </div>
            <span className="bg-emerald-950/40 text-emerald-400 border border-emerald-900/30 text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              {activeCount} {activeCount === 1 ? "student" : "students"} active
            </span>
          </div>

          <p className="text-xs text-slate-400 font-semibold leading-relaxed">
            Have questions about this lesson? Ask your peers, share learning tips, or help other students solve their challenges!
          </p>

          {/* Messages list */}
          <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2 mb-6 scrollbar-thin">
            {messages.map((msg) => (
              <div 
                key={msg.id} 
                className="bg-[#111827] border border-slate-800/80 rounded-2xl p-4 shadow-lg flex gap-4 animate-fade-in text-left"
              >
                {/* Avatar */}
                <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-sm ${
                  msg.name === "You" || msg.name === "Ammar Haider" || msg.name === getLoggedInUserInfo().name
                    ? "bg-gradient-to-tr from-blue-600 to-indigo-500" 
                    : "bg-gradient-to-tr from-cyan-500 to-blue-500"
                }`}>
                  {msg.avatar}
                </div>

                {/* Content */}
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-xs">
                      {msg.name}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">{getRelativeTime(msg)}</span>
                  </div>

                  {msg.replyTo && (
                    <div className="flex items-center gap-1 text-[9px] text-blue-400 font-mono font-bold uppercase mb-1 bg-blue-950/20 border border-blue-900/30 px-2 py-0.5 rounded-lg w-fit select-none">
                      <span>↩</span>
                      <span>replied to @{msg.replyTo}</span>
                    </div>
                  )}

                  <p className="text-xs text-slate-300 leading-relaxed break-words font-semibold">
                    {msg.text}
                  </p>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-1.5 select-none">
                    <button
                      onClick={() => handleLikeMessage(msg.id)}
                      disabled={likedMsgIds.includes(msg.id)}
                      className={`flex items-center gap-1 text-[10px] font-mono font-bold uppercase transition px-2 py-0.5 rounded border active:scale-95 ${
                        likedMsgIds.includes(msg.id)
                          ? "text-blue-400 bg-blue-950/20 border-blue-900/30 cursor-default"
                          : "text-slate-400 bg-[#070a13] hover:bg-blue-950/20 border-slate-800 hover:text-blue-400"
                      }`}
                    >
                      <span>👍</span>
                      <span>{msg.likes}</span>
                    </button>

                    <button
                      onClick={() => {
                        setReplyingTo(msg);
                        setNewMsg(`@${msg.name} `);
                        const textarea = document.getElementById("discussion-textarea");
                        if (textarea) {
                          textarea.focus();
                        }
                      }}
                      className="flex items-center gap-1 text-[10px] font-mono font-bold uppercase text-slate-400 hover:text-blue-400 bg-[#070a13] px-2 py-0.5 rounded border border-slate-800 active:scale-95 transition"
                    >
                      <span>💬 Reply</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {messages.length === 0 && (
              <div className="text-center py-8 text-slate-500 text-xs font-mono">
                No discussion messages yet. Be the first to start the conversation!
              </div>
            )}
          </div>

          {/* New message input */}
          <div className="bg-[#111827] border border-slate-800/80 rounded-2xl p-4">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-sm">
                {getLoggedInUserInfo().avatar}
              </div>
              <div className="flex-1 space-y-3">
                {replyingTo && (
                  <div className="flex items-center justify-between bg-blue-950/20 border border-blue-900/30 rounded-xl px-3 py-1.5 mb-3 text-[10px] font-mono font-bold text-blue-400 animate-fade-in select-none">
                    <div className="flex items-center gap-1.5">
                      <span>↩ Replying to</span>
                      <span className="text-white">@{replyingTo.name}</span>
                    </div>
                    <button 
                      onClick={() => {
                        setReplyingTo(null);
                        if (newMsg.startsWith(`@${replyingTo.name} `)) {
                          setNewMsg(newMsg.replace(`@${replyingTo.name} `, ""));
                        }
                      }}
                      className="text-blue-400 hover:text-blue-300 font-bold ml-2 text-xs"
                    >
                      ✕
                    </button>
                  </div>
                )}

                <textarea
                  id="discussion-textarea"
                  value={newMsg}
                  onChange={(e) => setNewMsg(e.target.value)}
                  placeholder="Share your thoughts or ask a question..."
                  rows="3"
                  className="w-full bg-[#070a13] border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500/50 outline-none resize-none transition-all font-mono"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <div className="flex justify-between items-center select-none">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Press <kbd className="font-mono bg-slate-900 px-1 py-0.5 rounded text-slate-400">Enter</kbd> to send
                  </span>
                  <button
                    onClick={handleSendMessage}
                    disabled={!newMsg.trim()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-extrabold uppercase font-mono tracking-wider text-[10px] px-4 py-2 rounded-xl transition shadow-md active:scale-95"
                  >
                    Post Comment
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE */}
      <div className="w-1/2 h-full flex flex-col bg-[#0b1220]">
        {/* EDITOR */}
        <div className="flex-1">
          {!started ? (
            <div className="flex items-center justify-center h-full text-slate-400">
              Click "Start Coding" to begin →
            </div>
          ) : (
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onMount={handleEditorDidMount}
              onChange={(val) => {
                setCode(val || "");
                setSubmitStatus("submit");
              }}
              options={{
                fontSize: 14,
                minimap: { enabled: true },
                wordWrap: "on",
              }}
            />
          )}
        </div>

        {/* BUTTON BAR */}
        {started && (
          <div className="flex items-center gap-3 p-3 border-t bg-[#0b1220]">
            <button
              className={`px-4 py-2 rounded-xl font-semibold transition-all ${
                submitStatus === "submitted"
                  ? "bg-green-600 text-white cursor-default"
                  : "bg-yellow-500 text-black hover:bg-yellow-600"
              }`}
              onClick={submitCode}
              disabled={loading || submitStatus === "submitted"}
            >
              {submitStatus === "submitted" ? "✓ Submitted" : "Submit"}
            </button>

            {submitStatus === "submitted" && hasNextLesson && (
              <button
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-semibold transition-all animate-pulse flex items-center gap-1"
                onClick={onNextLesson}
              >
                Next Lesson &rarr;
              </button>
            )}

            {submitStatus === "submitted" && !hasNextLesson && (
              <button
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl font-semibold transition-all animate-bounce flex items-center gap-1"
                onClick={onBack}
              >
                🎉 Course Completed! Back
              </button>
            )}

            <button
              className="bg-slate-700 text-white px-4 py-2 rounded-xl hover:bg-slate-600"
              onClick={runCode}
              disabled={loading}
            >
              Run
            </button>

            <button
              className="bg-slate-700 text-white px-4 py-2 rounded-xl hover:bg-slate-600"
              onClick={() => {
                setCode(lesson.solutionCode);
                setSubmitStatus("submit");
              }}
            >
              Solution
            </button>

            <button
              className="bg-slate-700 text-white px-4 py-2 rounded-xl hover:bg-slate-600"
              onClick={() => {
                setCode(lesson.starterCode);
                setSubmitStatus("submit");
              }}
            >
              ↺ Reset
            </button>
          </div>
        )}

        {/* RESPONSIVE TERMINAL */}
        {started && (
          <div className="flex flex-col bg-black border-t h-[180px]">
            {/* TERMINAL HEADER */}
            <div className="bg-[#121b2d] border-b border-slate-800 px-3 py-1.5 flex items-center justify-between text-[10px] font-mono text-slate-400 select-none">
              <span>APCRE Course Terminal (Python & Shell)</span>
              <span className="text-green-500 font-bold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                Live Connected
              </span>
            </div>

            {/* TERMINAL OUTPUT */}
            <div className="flex-1 text-green-400 text-xs p-3 font-mono overflow-auto whitespace-pre-wrap select-text animate-fade-in">
              {output || "APCRE Course Terminal Ready...\nOutput will appear here..."}
            </div>

            {/* TERMINAL INPUT */}
            <div className="bg-[#0b1220] border-t border-slate-800 p-2 flex gap-2">
              <span className="text-green-500 font-mono text-xs flex items-center">&gt;</span>
              <input
                type="text"
                placeholder="Type command (e.g. 'dir', 'python -V', 'ls') and press Enter..."
                className="flex-1 bg-transparent text-xs text-green-400 font-mono border-none outline-none"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const cmd = e.target.value;
                    if (cmd.trim()) {
                      runTerminalCommand(cmd);
                      e.target.value = "";
                    }
                  }
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* VIDEO TUTORIAL MODAL */}
      {showVideoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md transition-opacity">
          <div className="bg-[#0b1220] border border-slate-800 rounded-3xl overflow-hidden max-w-3xl w-full mx-4 shadow-2xl">
            {/* Modal Header */}
            <div className="bg-[#121b2d] border-b border-slate-800 px-6 py-4 flex items-center justify-between text-slate-200">
              <span className="font-semibold text-sm font-mono flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                Video Tutorial: {lesson.title}
              </span>
              <button
                onClick={() => setShowVideoModal(false)}
                className="text-slate-400 hover:text-white transition-colors text-lg"
              >
                ✕
              </button>
            </div>

            {/* Modal Body: Responsive Iframe Container */}
            <div className="relative pt-[56.25%] bg-black">
              <iframe
                className="absolute inset-0 w-full h-full border-none"
                src={lesson.videoUrl}
                title="Python Tutorial Video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              ></iframe>
            </div>

            {/* Modal Footer */}
            <div className="bg-[#121b2d] border-t border-slate-800 px-6 py-4 flex justify-between items-center text-xs text-slate-400">
              <span>Learn core concepts dynamically with APCRE Videos</span>
              <button
                onClick={() => setShowVideoModal(false)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-1.5 rounded-xl transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
