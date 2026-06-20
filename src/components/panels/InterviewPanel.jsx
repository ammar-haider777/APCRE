import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GraduationCap, Trophy, HelpCircle, Bot, Send, RotateCcw, Award } from "lucide-react";

export default function InterviewPanel() {
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState("dsa");
  const [sessionId, setSessionId] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  
  // Performance metrics
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [history, setHistory] = useState([]);
  
  const [answerInput, setAnswerInput] = useState("");
  const [feedback, setFeedback] = useState(null);

  // Start interview handler
  const handleStartInterview = async () => {
    setLoading(true);
    setFeedback(null);
    setAnswerInput("");
    try {
      const apiCategory = category === "systems" ? "system_design" : category;
      const res = await fetch("http://localhost:5001/api/interview/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: apiCategory })
      });
      const data = await res.json();
      if (data.session_id) {
        setSessionId(data.session_id);
        setCurrentQuestion(data.question);
        setDifficulty(data.difficulty || "beginner");
        setInterviewStarted(true);
        setScore(data.score || 0);
        setTotalQuestions(1);
        setHistory([]);
      } else if (data.error) {
        alert(data.error);
      }
    } catch (err) {
      alert("Failed to start technical interview session. Ensure the Flask AI server is online.");
    } finally {
      setLoading(false);
    }
  };

  // Submit answer handler
  const handleSubmitAnswer = async () => {
    if (!answerInput.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5001/api/interview/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, answer: answerInput })
      });
      const data = await res.json();
      if (data.success) {
        // scale score out of 100 to out of 10
        const earned = Math.round((data.score || 0) / 10);
        
        // Record history
        const newHistItem = {
          question: currentQuestion,
          answer: answerInput,
          scoreEarned: earned,
          feedback: data.feedback,
          correct: earned >= 7
        };
        setHistory(prev => [newHistItem, ...prev]);

        setScore(prev => prev + earned * 10);
        setFeedback({
          scoreEarned: earned,
          evaluation: data.feedback,
          suggestion: data.correct_answer ? `Model Answer: ${data.correct_answer}` : "Excellent work! Keep your definitions clear and concise."
        });

        // Set next question or handle completion
        if (data.interview_complete) {
          setCurrentQuestion("🎉 Congratulations! You have completed the technical interview session.");
        } else if (data.next_question) {
          setCurrentQuestion(data.next_question.question || "");
          setDifficulty(data.next_question.difficulty || "beginner");
          setTotalQuestions(prev => prev + 1);
        }
        setAnswerInput("");
      }
    } catch (err) {
      alert("Failed to evaluate answer. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const difficultyColors = {
    beginner: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
    intermediate: "bg-amber-500/10 border-amber-500/20 text-amber-400",
    advanced: "bg-rose-500/10 border-rose-500/20 text-rose-400"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35 }}
      className="space-y-6 text-slate-200"
    >
      {/* 1. Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <GraduationCap className="h-6 w-6 text-blue-500" />
            <span>AI Technical Interview Workspace</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Adaptive, stateful interview assessor evaluating DSA, OOP, Systems, and Code Review metrics.</p>
        </div>
      </div>

      {/* 2. Start view vs. Active view */}
      <AnimatePresence mode="wait">
        {!interviewStarted ? (
          <motion.div
            key="start-pane"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="max-w-md mx-auto rounded-2xl border border-slate-850 bg-[#111827] p-6 shadow-xl flex flex-col items-center text-center space-y-6"
          >
            <div className="p-4 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Bot className="h-10 w-10 animate-bounce" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Initiate CS Interview session</h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                APCRE will start an adaptive interview session. Difficulty levels will scale based on the depth of your technical responses.
              </p>
            </div>

            {/* Category selection */}
            <div className="w-full space-y-2">
              <label className="text-[10px] uppercase font-mono font-bold text-slate-500 block text-left">Interview Domain</label>
              <div className="grid grid-cols-3 gap-2">
                {["dsa", "oop", "systems"].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setCategory(cat)}
                    className={`py-2 rounded-xl text-xs font-semibold border font-mono uppercase tracking-wider transition-all duration-300 ${
                      category === cat
                        ? "bg-blue-500/15 border-blue-500/40 text-blue-400"
                        : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleStartInterview}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-xs font-bold text-white shadow-md hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg transition-all duration-300 disabled:opacity-50"
            >
              {loading ? "Initializing Session..." : "Launch Interview"}
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="interview-pane"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="grid grid-cols-1 lg:grid-cols-5 gap-6"
          >
            {/* QA Conversation Workspace (3 cols) */}
            <div className="lg:col-span-3 rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex flex-col justify-between min-h-[400px]">
              <div className="space-y-5 flex-1">
                {/* Question bubble */}
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex gap-3">
                  <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 h-9 w-9 shrink-0 flex items-center justify-center">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 font-mono uppercase tracking-wide">APCRE Evaluator ({totalQuestions} / 5)</div>
                    <p className="text-xs text-slate-200 mt-2 font-mono leading-relaxed">{currentQuestion}</p>
                  </div>
                </div>

                {/* Feedback Bubble if available */}
                {feedback && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/15 flex gap-3"
                  >
                    <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 h-9 w-9 shrink-0 flex items-center justify-center">
                      <Award className="h-5 w-5" />
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] text-slate-500 font-mono uppercase tracking-wide">Evaluator Response Assessment</div>
                      <div className="text-xs font-bold text-emerald-400 font-mono mt-1">Score: {feedback.scoreEarned} / 10</div>
                      <p className="text-[11px] text-slate-400 leading-normal mt-2">{feedback.evaluation}</p>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Answer input */}
              <div className="mt-6 flex items-center gap-3">
                <textarea
                  value={answerInput}
                  onChange={(e) => setAnswerInput(e.target.value)}
                  placeholder="Type your technical answer here..."
                  className="flex-1 rounded-xl bg-slate-950/60 border border-slate-850 px-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500/50 focus:outline-none resize-none h-[50px] font-mono"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmitAnswer();
                    }
                  }}
                />
                <button
                  onClick={handleSubmitAnswer}
                  disabled={loading || !answerInput.trim()}
                  className="rounded-xl bg-blue-600 hover:bg-blue-700 p-3.5 text-white transition-all disabled:opacity-50"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Performance status & Scorecard sidebar (2 cols) */}
            <div className="lg:col-span-2 space-y-4">
              
              {/* Score card */}
              <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    <Trophy className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-mono uppercase tracking-wider">Active Score</div>
                    <div className="text-2xl font-bold text-white font-mono mt-0.5">{score} pts</div>
                  </div>
                </div>
                <div className={`px-3 py-1 border rounded-full text-[9px] font-mono uppercase font-bold ${difficultyColors[difficulty]}`}>
                  {difficulty}
                </div>
              </div>

              {/* Session History */}
              <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex flex-col min-h-[300px]">
                <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
                  <RotateCcw className="h-4 w-4 text-blue-400" />
                  <span>Session History Logs</span>
                </h3>
                <div className="flex-1 space-y-3 overflow-y-auto max-h-[220px] pr-1">
                  {history.length > 0 ? (
                    history.map((hist, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-850 text-[10px] space-y-2 leading-relaxed">
                        <div className="font-semibold text-slate-200 truncate">{hist.question}</div>
                        <div className="text-slate-500 truncate">Your answer: {hist.answer}</div>
                        <div className="flex justify-between items-center text-[9px] border-t border-slate-800 pt-1.5 font-mono">
                          <span className={hist.correct ? "text-emerald-400" : "text-rose-400"}>
                            {hist.correct ? "Excellent response" : "Conceptual gaps found"}
                          </span>
                          <span className="text-slate-400">Score: {hist.scoreEarned} / 10</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center text-center py-16 text-slate-500 text-xs">
                      No logs in current session.
                    </div>
                  )}
                </div>
              </div>
              
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
