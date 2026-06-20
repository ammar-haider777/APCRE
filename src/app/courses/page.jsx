"use client";
// src/learning/LearningLayout.jsx
import React, { useState } from "react";
import CoursesPage from '@/learning/CoursesPage';
import LessonPage from '@/learning/LessonPage';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { GraduationCap, ArrowLeft, Trophy, CheckCircle2, Lock } from "lucide-react";
import { motion } from "framer-motion";

export default function LearningLayout() {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [completedChapters, setCompletedChapters] = useState([]);

  /* ================= COURSES DATA ================= */
  const courses = [
    {
      id: 1,
      title: "Python Fundamentals & Syntax",
      chapters: [
        {
          id: 1,
          title: "Chapter 1: Variables & Print",
          introduction: "In Python, variables store data values and are created the moment you first assign a value to them using the '=' operator. The 'print()' function displays the value on the console screen.",
          exampleCode: "# Example:\nname = \"Ammar\"\nprint(name)",
          task: "Create a variable named 'x' with the value 10, then print it using the print() function.",
          starterCode: "# Create variable 'x' and print it below\n",
          solutionCode: "x = 10\nprint(x)",
          expectedOutput: "10",
          videoUrl: "https://www.youtube.com/embed/kqtD5dpn9C8"
        },
        {
          id: 2,
          title: "Chapter 2: Arithmetic Operators",
          introduction: "Python supports standard mathematical arithmetic: addition (+), subtraction (-), multiplication (*), and division (/). You can perform these inside print() or assign them to variables first.",
          exampleCode: "# Example:\na = 5\nb = 3\nprint(a + b)",
          task: "Multiply 7 and 8 together and print the resulting product directly.",
          starterCode: "# Write code below to print the product of 7 and 8\n",
          solutionCode: "print(7 * 8)",
          expectedOutput: "56",
          videoUrl: "https://www.youtube.com/embed/khKvIO-G4kU"
        },
        {
          id: 3,
          title: "Chapter 3: String Manipulation",
          introduction: "Strings are sequences of characters wrapped in quotes. You can concatenate (join) strings together using the '+' arithmetic operator.",
          exampleCode: "# Example:\ngreeting = \"Hello \" + \"World\"\nprint(greeting)",
          task: "Join the string 'Python' with a single space ' ' and the string 'Developer', then print the concatenated result.",
          starterCode: "# Concatenate 'Python' and 'Developer' with a space and print it\n",
          solutionCode: "print(\"Python\" + \" \" + \"Developer\")",
          expectedOutput: "Python Developer",
          videoUrl: "https://www.youtube.com/embed/kqtD5dpn9C8"
        },
        {
          id: 4,
          title: "Chapter 4: Lists & Indexing",
          introduction: "Lists are used to store multiple items in a single variable. Items are ordered, indexable starting at 0, and changeable.",
          exampleCode: "# Example:\nfruits = [\"apple\", \"banana\", \"cherry\"]\nprint(fruits[0]) # Prints 'apple'",
          task: "Create a list named 'colors' containing 'red', 'green', and 'blue'. Then, print the second element (index 1).",
          starterCode: "# Create list 'colors' and print the item at index 1\n",
          solutionCode: "colors = [\"red\", \"green\", \"blue\"]\nprint(colors[1])",
          expectedOutput: "green",
          videoUrl: "https://www.youtube.com/embed/W8KRzm-HUcc"
        },
        {
          id: 5,
          title: "Chapter 5: Conditionals (If-Else)",
          introduction: "Conditional statements evaluate conditions as True or False. Python uses 'if' and 'else' statements to execute branches of code dynamically based on evaluation.",
          exampleCode: "# Example:\nage = 18\nif age >= 18:\n    print(\"Adult\")\nelse:\n    print(\"Minor\")",
          task: "Create a variable named 'score' equal to 85. If 'score' is greater than 80, print 'Pass', otherwise print 'Fail'.",
          starterCode: "# Define score = 85 and write an if-else statement to print Pass/Fail\n",
          solutionCode: "score = 85\nif score > 80:\n    print(\"Pass\")\nelse:\n    print(\"Fail\")",
          expectedOutput: "Pass",
          videoUrl: "https://www.youtube.com/embed/DZwmZ8UqEQQ"
        },
        {
          id: 6,
          title: "Chapter 6: For Loops & Iteration",
          introduction: "A 'for' loop is used to iterate over a sequence (such as a list, string, or range). The code inside the loop block is executed once for each item in the sequence, allowing you to automate repetitive tasks.",
          exampleCode: "# Example:\nfruits = [\"apple\", \"banana\"]\nfor f in fruits:\n    print(f)",
          task: "Create a list named 'numbers' containing the integers 1, 2, and 3. Write a for loop that iterates through 'numbers' and prints the string 'item ' concatenated with each number (e.g. 'item 1').",
          starterCode: "# Create list 'numbers' and write a for loop to print item 1, item 2, etc.\n",
          solutionCode: "numbers = [1, 2, 3]\nfor n in numbers:\n    print(\"item \" + str(n))",
          expectedOutput: "item 1\nitem 2\nitem 3",
          videoUrl: "https://www.youtube.com/embed/6iF8Xb7Z3wQ"
        },
        {
          id: 7,
          title: "Chapter 7: Functions & Parameters",
          introduction: "A function is a reusable block of code that only runs when it is called. You can pass inputs, known as 'parameters', into a function. Functions are defined using the 'def' keyword followed by the function name.",
          exampleCode: "# Example:\ndef greet_user(name):\n    print(\"Hello \" + name)\n\ngreet_user(\"Ammar\")",
          task: "Define a function named 'greet' that takes one parameter named 'name'. Inside the function, print 'Hello ' concatenated with the parameter. Call the function and pass the string 'Ammar' as an argument.",
          starterCode: "# Define the greet function and call it passing 'Ammar' below\n",
          solutionCode: "def greet(name):\n    print(\"Hello \" + name)\n\ngreet(\"Ammar\")",
          expectedOutput: "Hello Ammar",
          videoUrl: "https://www.youtube.com/embed/9Os0o3wzS_I"
        },
        {
          id: 8,
          title: "Chapter 8: Dictionaries (Key-Value Pairs)",
          introduction: "Dictionaries are used to store data values in key-value pairs. A dictionary is a collection which is ordered, changeable, and does not allow duplicate keys. It is written using curly braces {}.",
          exampleCode: "# Example:\nstudent = {\n    \"name\": \"Ammar\",\n    \"grade\": \"A\"\n}\nprint(student[\"name\"]) # Prints 'Ammar'",
          task: "Create a dictionary named 'user_profile' with keys 'username' equal to 'Ammar' and 'role' equal to 'Developer'. Print the value associated with the key 'username'.",
          starterCode: "# Create 'user_profile' dictionary and print the value of 'username' below\n",
          solutionCode: "user_profile = {\n    \"username\": \"Ammar\",\n    \"role\": \"Developer\"\n}\nprint(user_profile[\"username\"])",
          expectedOutput: "Ammar",
          videoUrl: "https://www.youtube.com/embed/daefaL5Nq7k"
        }
      ]
    },
    {
      id: 2,
      title: "AI & Machine Learning Basics",
      chapters: [
        {
          id: 1,
          title: "Chapter 1: NumPy Arrays",
          introduction: "NumPy is the cornerstone package for scientific computing in Python. It provides the N-dimensional array object used for numerical operations.",
          exampleCode: "# Example:\nimport numpy as np\narr = np.array([1, 2, 3])\nprint(arr)",
          task: "Import the 'numpy' package as 'np'. Create a NumPy array from the list [10, 20, 30] and print it.",
          starterCode: "# Import numpy as np and print the array [10, 20, 30]\n",
          solutionCode: "import numpy as np\narr = np.array([10, 20, 30])\nprint(arr)",
          expectedOutput: "[10 20 30]",
          videoUrl: "https://www.youtube.com/embed/GB9ByJvsuLI"
        },
        {
          id: 2,
          title: "Chapter 2: ML Model Architecture",
          introduction: "Supervised models learn patterns from labeled datasets. Scikit-learn offers class estimators that conform to a unified fit/predict API structure.",
          exampleCode: "# Example:\nfrom sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression()\n# fit model and predict",
          task: "Print the string 'Model Trained' to represent a successful ML model training completion.",
          starterCode: "# Print 'Model Trained'\n",
          solutionCode: "print(\"Model Trained\")",
          expectedOutput: "Model Trained",
          videoUrl: "https://www.youtube.com/embed/7eh4d6sabA0"
        }
      ]
    },
    {
      id: 3,
      title: "Object-Oriented Programming",
      chapters: [
        {
          id: 1,
          title: "Chapter 1: Class Definition",
          introduction: "A Class is like an object constructor, or a 'blueprint' for creating objects in Python.",
          exampleCode: "# Example:\nclass Person:\n  def __init__(self, name):\n    self.name = name\n\np1 = Person('John')\nprint(p1.name)",
          task: "Create a class named 'MyClass' with a property 'x' equal to 5. Instanciate it and print the property 'x' of that instance.",
          starterCode: "# Create class MyClass and print instance's x property\n",
          solutionCode: "class MyClass:\n  x = 5\n\np = MyClass()\nprint(p.x)",
          expectedOutput: "5",
          videoUrl: "https://www.youtube.com/embed/ZDa-Z5JzLYM"
        },
      ],
    },
  ];

  /* ================= PROGRESS ================= */
  const progress =
    selectedCourse?.chapters?.length > 0
      ? (completedChapters.length / selectedCourse.chapters.length) * 100
      : 0;

  /* ================= MARK COMPLETE ================= */
  const markComplete = (chapterId) => {
    setCompletedChapters((prev) => {
      if (prev.includes(chapterId)) return prev;
      return [...prev, chapterId];
    });
  };

  /* ================= COURSE SELECT ================= */
  const handleSelectCourse = (course) => {
    const realCourse = courses.find((c) => c.id === course.id);
    if (!realCourse) {
      console.error("Course not found");
      return;
    }
    setSelectedCourse(realCourse);
    setSelectedChapter(null);
    setCompletedChapters([]);
  };

  let content;

  if (!selectedCourse) {
    content = <CoursesPage onSelectCourse={handleSelectCourse} />;
  } else if (!selectedCourse?.chapters) {
    content = <div className="p-8 text-slate-400 font-mono">⚠️ No chapters found</div>;
  } else if (!selectedChapter) {
    content = (
      <div className="max-w-4xl mx-auto p-8 text-left space-y-6 text-slate-200">
        <button
          onClick={() => setSelectedCourse(null)}
          className="inline-flex items-center gap-1 text-xs font-bold uppercase font-mono tracking-wider text-blue-400 hover:text-blue-300 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Courses</span>
        </button>

        <div className="border-b border-slate-800 pb-4">
          <h1 className="text-2xl font-bold text-white tracking-tight">{selectedCourse.title}</h1>
          
          {/* PROGRESS BAR */}
          <div className="mt-4 p-4 rounded-2xl bg-[#111827] border border-slate-800/80 shadow-md">
            <div className="flex justify-between text-xs font-mono font-bold text-slate-400 mb-2 uppercase tracking-wide">
              <span>Course Progress</span>
              <span className="text-emerald-400">{Math.round(progress)}% Completed</span>
            </div>

            <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden">
              <div
                className="h-2.5 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {/* CHAPTER LIST */}
        <div className="space-y-3">
          {selectedCourse.chapters.map((ch, index) => {
            const unlocked =
              index === 0 ||
              completedChapters.includes(
                selectedCourse.chapters[index - 1]?.id,
              );

            return (
              <button
                key={ch.id}
                onClick={() => unlocked && setSelectedChapter(ch)}
                disabled={!unlocked}
                className={`w-full p-4 border rounded-2xl flex justify-between items-center text-xs font-mono transition-all duration-300 ${
                  unlocked
                    ? "bg-[#111827] border-slate-800 text-slate-200 hover:border-slate-700 cursor-pointer shadow-md"
                    : "bg-slate-950/20 border-slate-900/60 text-slate-600 cursor-not-allowed opacity-50"
                }`}
              >
                <span className="font-semibold text-left">
                  Chapter {ch.id}: {ch.title}
                </span>

                <div className="flex items-center gap-2 shrink-0">
                  {!unlocked && <Lock className="h-4 w-4 text-slate-600" />}

                  {completedChapters.includes(ch.id) && (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  } else {
    const currentChapterIndex = selectedCourse.chapters.findIndex(ch => ch.id === selectedChapter.id);
    const nextChapter = selectedCourse.chapters[currentChapterIndex + 1];

    content = (
      <LessonPage
        key={selectedChapter.id}
        lesson={selectedChapter}
        onBack={() => setSelectedChapter(null)}
        onComplete={() => markComplete(selectedChapter.id)}
        hasNextLesson={!!nextChapter}
        onNextLesson={() => {
          markComplete(selectedChapter.id);
          setSelectedChapter(nextChapter);
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200 overflow-x-hidden selection:bg-blue-500/30">
      <Header />
      <main className="flex-grow">
        {content}
      </main>
      {!selectedChapter && <Footer />}
    </div>
  );
}
