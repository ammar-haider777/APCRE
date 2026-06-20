import React from "react";
import { BookOpen, Sparkles, GraduationCap } from "lucide-react";
import { motion } from "framer-motion";

export default function CoursesPage({ onSelectCourse }) {
  const courses = [
    {
      id: 1,
      title: "Python Fundamentals & Syntax",
      level: "Beginner",
      description: "Learn Python from variables, printing, operators, strings, lists, conditionals, loops, and reusable functions.",
    },
    {
      id: 2,
      title: "AI & Machine Learning Basics",
      level: "Intermediate",
      description: "Explore numpy array computations, scientific matrix operations, and supervised Scikit-learn architectures.",
    },
    {
      id: 3,
      title: "Object-Oriented Programming",
      level: "Advanced",
      description: "Understand classes, blueprints, __init__ constructor properties, and object instantiation patterns.",
    },
  ];

  return (
    <div className="max-w-5xl mx-auto p-8 text-left space-y-6 text-slate-200">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <GraduationCap className="h-6 w-6 text-blue-500" />
          <span>Interactive Academy Courses</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-semibold">
          Select an interactive domain below to begin solving hands-on python challenges side-by-side with our compiler.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        {courses.map((course) => {
          let lvlColor = "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
          if (course.level === "Intermediate") lvlColor = "bg-amber-500/10 border-amber-500/20 text-amber-400";
          else if (course.level === "Advanced") lvlColor = "bg-rose-500/10 border-rose-500/20 text-rose-400";

          return (
            <motion.div
              key={course.id}
              onClick={() => onSelectCourse(course)}
              whileHover={{ scale: 1.01 }}
              className="cursor-pointer rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg hover:border-blue-500/40 hover:shadow-xl hover:shadow-blue-500/5 transition duration-300 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className={`px-2.5 py-0.5 border text-[9px] font-bold font-mono rounded-full uppercase shrink-0 ${lvlColor}`}>
                    {course.level}
                  </div>
                  <BookOpen className="h-4 w-4 text-slate-500" />
                </div>
                <h2 className="text-base font-bold text-white tracking-tight leading-snug">{course.title}</h2>
                <p className="text-xs text-slate-400 leading-relaxed font-semibold">{course.description}</p>
              </div>

              <div className="mt-6 flex items-center gap-1.5 text-[10px] font-bold font-mono uppercase tracking-wider text-blue-400">
                <span>Start Learning</span>
                <ChevronRightSymbol className="w-3.5 h-3.5" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

function ChevronRightSymbol(props) {
  return (
    <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}
