import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import bcrypt from "bcrypt";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import archiver from "archiver";
import multer from "multer";
import unzipper from "unzipper";
import { fileURLToPath } from "url";

/*  NEW: socket.io + http */
import http from "http";
import { Server } from "socket.io";

dotenv.config();

const app = express();

/* =========================================================
   CORS
   ========================================================= */
app.use(
  cors({
    origin: "*", // allow all domains to hit the api in development
    methods: ["GET", "POST", "PUT", "DELETE"],
  }),
);

app.use(express.json({ limit: "10mb" }));

/* =========================================================
   FIX: __dirname in ES Modules
   ========================================================= */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/* =========================================================
   Serve Static Files (Images like /Ammar.jpg)
   ========================================================= */
app.use(express.static(path.join(__dirname, "public")));

/* =========================================================
   Workspace folder (real files stored here)
   ========================================================= */
let WORKSPACE_DIR = path.join(__dirname, "workspace");

if (!fs.existsSync(WORKSPACE_DIR)) {
  fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
}

/* =========================================================
   Helpers
   ========================================================= */

// prevent "../" hacking
function safeJoin(base, targetPath) {
  const target = targetPath.replaceAll("\\", "/");
  const resolved = path.resolve(base, target);
  if (!resolved.startsWith(base)) {
    throw new Error("Invalid path (security blocked)");
  }
  return resolved;
}

// List of directories to ignore
const IGNORED_DIRS = new Set([
  "node_modules",
  ".git",
  ".venv",
  "venv",
  "env",
  "dist",
  "build",
  "__pycache__",
  ".idea",
  ".vscode",
  "tmp",
]);

// List of binary extensions to not read
const BINARY_EXTENSIONS = new Set([
  "zip", "rar", "tar", "gz", "7z", "png", "jpg", "jpeg",
  "gif", "ico", "pdf", "exe", "dll", "so", "dylib", "bin",
  "pyc", "db", "sqlite", "mp3", "mp4", "wav", "avi", "mov",
  "woff", "woff2", "ttf", "eot"
]);

// read all files and directories recursively
function listAllFiles(dir, baseDir = WORKSPACE_DIR) {
  const results = [];
  
  if (!fs.existsSync(dir)) return results;

  let items = [];
  try {
    items = fs.readdirSync(dir, { withFileTypes: true });
  } catch (err) {
    console.error(`Failed to read directory ${dir}:`, err.message);
    return results;
  }

  for (const item of items) {
    // Skip ignored directories
    if (item.isDirectory() && IGNORED_DIRS.has(item.name)) {
      continue;
    }

    const fullPath = path.join(dir, item.name);
    const relativePath = path.relative(baseDir, fullPath).replaceAll("\\", "/");

    if (item.isDirectory()) {
      results.push({
        name: item.name,
        path: relativePath,
        isDirectory: true
      });
      results.push(...listAllFiles(fullPath, baseDir));
    } else {
      // Check file extension
      const ext = path.extname(item.name).toLowerCase().replace(".", "");
      
      // Check file size
      let size = 0;
      try {
        const stats = fs.statSync(fullPath);
        size = stats.size;
      } catch (e) {}

      // If it's binary or too large, don't read content
      const isBinary = BINARY_EXTENSIONS.has(ext);
      const isTooLarge = size > 1024 * 1024; // 1MB

      let content = "";
      if (!isBinary && !isTooLarge) {
        try {
          content = fs.readFileSync(fullPath, "utf8");
        } catch (err) {
          console.error(`Failed to read file ${fullPath}:`, err.message);
          content = `(Error reading file: ${err.message})`;
        }
      } else if (isBinary) {
        content = "(Binary file)";
      } else {
        content = "(File too large to display)";
      }

      results.push({
        name: item.name,
        path: relativePath,
        content: content,
        isDirectory: false
      });
    }
  }

  return results;
}

/* =========================================================
   AI Engine URL (Flask backend)
   ========================================================= */
const AI_ENGINE_URL = process.env.AI_ENGINE_URL || "http://localhost:5001";

/* =========================================================
    NEW: HTTP SERVER + SOCKET.IO
   ========================================================= */
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

/* =========================================================
    NEW: Rooms storage (in-memory)
   ========================================================= */
// rooms = {
//   roomId: {
//     users: [{ socketId, name, email }],
//     code: "latest code"
//   }
// }
const rooms = {};

/* =========================================================
    NEW: Socket.IO events
   ========================================================= */
io.on("connection", (socket) => {
  console.log("🟢 Socket connected:", socket.id);

  // Join room
  socket.on("room:join", ({ roomId, user }) => {
    try {
      if (!roomId) return;

      socket.join(roomId);

      if (!rooms[roomId]) {
        rooms[roomId] = { users: [], code: "" };
      }

      // add user
      rooms[roomId].users.push({
        socketId: socket.id,
        name: user?.name || "Guest",
        email: user?.email || "guest@email.com",
      });

      console.log(` ${socket.id} joined room ${roomId}`);

      // send room info to new user
      socket.emit("room:joined", {
        roomId,
        users: rooms[roomId].users,
        code: rooms[roomId].code,
      });

      // notify others
      socket.to(roomId).emit("room:userJoined", {
        socketId: socket.id,
        name: user?.name || "Guest",
      });

      // update users list for all
      io.to(roomId).emit("room:users", rooms[roomId].users);
    } catch (err) {
      socket.emit("room:error", { error: err.message });
    }
  });

  // Leave room
  socket.on("room:leave", ({ roomId }) => {
    try {
      if (!roomId) return;

      socket.leave(roomId);

      if (rooms[roomId]) {
        rooms[roomId].users = rooms[roomId].users.filter(
          (u) => u.socketId !== socket.id,
        );

        io.to(roomId).emit("room:users", rooms[roomId].users);

        socket.to(roomId).emit("room:userLeft", {
          socketId: socket.id,
        });

        if (rooms[roomId].users.length === 0) {
          delete rooms[roomId];
        }
      }
    } catch (err) {
      socket.emit("room:error", { error: err.message });
    }
  });

  // Real-time Code Sync
  socket.on("code:update", ({ roomId, code }) => {
    try {
      if (!roomId) return;

      if (!rooms[roomId]) {
        rooms[roomId] = { users: [], code: "" };
      }

      rooms[roomId].code = code;

      // send updated code to others
      socket.to(roomId).emit("code:updated", { code });
    } catch (err) {
      socket.emit("room:error", { error: err.message });
    }
  });

  // WebRTC Signaling Relay
  socket.on("rtc:signal", ({ roomId, signal }) => {
    try {
      console.log(`📡 rtc:signal received on server from ${socket.id} for room ${roomId}`);
      if (!roomId) return;
      socket.to(roomId).emit("rtc:signal", { sender: socket.id, signal });
    } catch (err) {
      console.error("rtc:signal error:", err);
      socket.emit("room:error", { error: err.message });
    }
  });

  // WebRTC Leave Call relay
  socket.on("rtc:leave-call", ({ roomId }) => {
    try {
      console.log(`🔇 rtc:leave-call received on server from ${socket.id} for room ${roomId}`);
      if (!roomId) return;
      socket.to(roomId).emit("rtc:leave-call");
    } catch (err) {
      console.error("rtc:leave-call error:", err);
      socket.emit("room:error", { error: err.message });
    }
  });


  // Real-time Chat (optional)
  socket.on("chat:send", ({ roomId, message, user }) => {
    try {
      if (!roomId || !message) return;

      io.to(roomId).emit("chat:receive", {
        message,
        user: user?.name || "Guest",
        time: new Date().toLocaleTimeString(),
      });
    } catch (err) {
      socket.emit("room:error", { error: err.message });
    }
  });

  // Disconnect cleanup
  socket.on("disconnect", () => {
    console.log("🔴 Socket disconnected:", socket.id);

    for (const roomId of Object.keys(rooms)) {
      const before = rooms[roomId].users.length;

      rooms[roomId].users = rooms[roomId].users.filter(
        (u) => u.socketId !== socket.id,
      );

      const after = rooms[roomId].users.length;

      if (before !== after) {
        io.to(roomId).emit("room:users", rooms[roomId].users);
        socket.to(roomId).emit("room:userLeft", { socketId: socket.id });

        if (rooms[roomId].users.length === 0) {
          delete rooms[roomId];
        }
      }
    }
  });
});

/* =========================================================
   Health check
   ========================================================= */
app.get("/", (req, res) => {
  res.send(" APCRE Backend is running...");
});

/* =========================================================
   USER ACCOUNT API (Auth & Profile)
   ========================================================= */
const USERS_FILE = path.join(__dirname, "users.json");

// Ensure public avatars directory exists
fs.mkdirSync(path.join(__dirname, "public/avatars"), { recursive: true });

const storage = multer.diskStorage({
  destination: path.join(__dirname, "public/avatars"),
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  },
});
const upload = multer({ storage });

app.use("/avatars", express.static(path.join(__dirname, "public/avatars")));

const getUsers = () => {
  if (fs.existsSync(USERS_FILE)) return JSON.parse(fs.readFileSync(USERS_FILE, "utf8"));
  return [];
};
const saveUsers = (users) => fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));

app.post("/api/signup", upload.single("avatar"), async (req, res) => {
  try {
    const { firstName, lastName, email, password } = req.body;
    let users = getUsers();

    if (users.find(u => u.email === email)) {
      return res.status(400).json({ error: "Email already exists" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = {
      id: Date.now().toString(),
      firstName,
      lastName,
      email,
      password: hashedPassword,
      progress: [],
      avatar: req.file ? `/avatars/${req.file.filename}` : `https://ui-avatars.com/api/?name=${encodeURIComponent(firstName + " " + lastName)}&background=random`
    };

    users.push(newUser);
    saveUsers(users);

    const userResponse = { ...newUser };
    delete userResponse.password;
    res.json({ message: "Signup successful", user: userResponse });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const users = getUsers();
    const user = users.find(u => u.email === email);

    if (!user) return res.status(401).json({ error: "Invalid email or password" });

    // Support both hashed (bcrypt) and legacy plain-text passwords
    let passwordMatch = false;
    if (user.password.startsWith("$2")) {
      passwordMatch = await bcrypt.compare(password, user.password);
    } else {
      passwordMatch = (password === user.password);
    }

    if (!passwordMatch) return res.status(401).json({ error: "Invalid email or password" });

    const userResponse = { ...user };
    delete userResponse.password;
    res.json({ message: "Login successful", user: userResponse });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/progress", (req, res) => {
  try {
    const { userId, taskId } = req.body;
    let users = getUsers();
    let index = users.findIndex(u => u.id === userId);
    if (index !== -1) {
      if (!users[index].progress) users[index].progress = [];
      if (!users[index].progress.includes(taskId)) {
        users[index].progress.push(taskId);
        saveUsers(users);
      }
      const userResponse = { ...users[index] };
      delete userResponse.password;
      res.json({ success: true, user: userResponse });
    } else {
      res.status(404).json({ error: "User not found" });
    }
  } catch(err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/user", (req, res) => {
  const email = req.query.email;
  if (email) {
    const users = getUsers();
    const user = users.find(u => u.email === email);
    if (user) {
      const userResponse = { ...user };
      delete userResponse.password;
      return res.json(userResponse);
    }
  }
  res.status(401).json({ error: "Not authenticated" });
});

app.get("/api/active-users", (req, res) => {
  try {
    const activeCount = io.sockets.sockets.size || 1;
    res.json({ activeCount });
  } catch (err) {
    res.json({ activeCount: 1 });
  }
});

/* =========================================================
   CONTACT & NEWSLETTER HTTP APIs
   ========================================================= */

const CONTACTS_FILE = path.join(__dirname, "contacts.json");
const SUBSCRIBERS_FILE = path.join(__dirname, "subscribers.json");

app.post("/api/contact", (req, res) => {
  try {
    const { firstName, lastName, email, phone, topic, helpType, message, agreePolicy } = req.body;

    if (!firstName || !email || !message) {
      return res.status(400).json({ error: "First name, email, and message are required." });
    }

    const newContact = {
      id: Date.now().toString(),
      firstName,
      lastName: lastName || "",
      email,
      phone: phone || "",
      topic: topic || "",
      helpType: helpType || "",
      message,
      agreePolicy: !!agreePolicy,
      date: new Date().toISOString()
    };

    let contacts = [];
    if (fs.existsSync(CONTACTS_FILE)) {
      contacts = JSON.parse(fs.readFileSync(CONTACTS_FILE, "utf8"));
    }
    contacts.push(newContact);
    fs.writeFileSync(CONTACTS_FILE, JSON.stringify(contacts, null, 2));

    res.status(200).json({ message: "Thank you! Your message has been sent successfully." });
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.post("/api/subscribe", (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ error: "Email is required." });
    }

    const newSubscriber = {
      id: Date.now().toString(),
      email,
      date: new Date().toISOString()
    };

    let subscribers = [];
    if (fs.existsSync(SUBSCRIBERS_FILE)) {
      subscribers = JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, "utf8"));
    }
    subscribers.push(newSubscriber);
    fs.writeFileSync(SUBSCRIBERS_FILE, JSON.stringify(subscribers, null, 2));

    res.status(200).json({ message: "Subscribed successfully!" });
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
});

/* =========================================================
   FILE APIs (REAL FILE SYSTEM)
   ========================================================= */

app.get("/api/files", (req, res) => {
  try {
    const files = listAllFiles(WORKSPACE_DIR);
    res.json({ files });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/files", (req, res) => {
  try {
    const { path: filePath, content } = req.body;

    if (!filePath) return res.status(400).json({ error: "Path required" });

    const fullPath = safeJoin(WORKSPACE_DIR, filePath);

    fs.mkdirSync(path.dirname(fullPath), { recursive: true });

    if (fs.existsSync(fullPath)) {
      return res.status(400).json({ error: "File already exists" });
    }

    fs.writeFileSync(fullPath, content || "", "utf8");

    res.json({
      message: "File created",
      file: {
        name: path.basename(fullPath),
        path: filePath.replaceAll("\\", "/"),
        content: content || "",
      },
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put("/api/files", (req, res) => {
  try {
    const { path: filePath, content } = req.body;
    if (!filePath) return res.status(400).json({ error: "Path required" });

    const fullPath = safeJoin(WORKSPACE_DIR, filePath);

    if (!fs.existsSync(fullPath)) {
      return res.status(404).json({ error: "File not found" });
    }

    fs.writeFileSync(fullPath, content || "", "utf8");

    res.json({ message: " File saved" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete("/api/files", (req, res) => {
  try {
    const { path: filePath } = req.body;
    if (!filePath) return res.status(400).json({ error: "Path required" });

    const fullPath = safeJoin(WORKSPACE_DIR, filePath);

    if (!fs.existsSync(fullPath)) {
      return res.status(404).json({ error: "File not found" });
    }

    fs.unlinkSync(fullPath);

    res.json({ message: "🗑 File deleted" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put("/api/files/rename", (req, res) => {
  try {
    const { oldPath, newPath } = req.body;
    if (!oldPath || !newPath)
      return res.status(400).json({ error: "oldPath & newPath required" });

    const oldFull = safeJoin(WORKSPACE_DIR, oldPath);
    const newFull = safeJoin(WORKSPACE_DIR, newPath);

    if (!fs.existsSync(oldFull)) {
      return res.status(404).json({ error: "Old file not found" });
    }

    fs.mkdirSync(path.dirname(newFull), { recursive: true });

    fs.renameSync(oldFull, newFull);

    res.json({ message: " File renamed" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* =========================================================
   ADDITIONAL WORKSPACE & FOLDER APIs
   ========================================================= */

// Create a new folder
app.post("/api/folders", (req, res) => {
  try {
    const { path: folderPath } = req.body;
    if (!folderPath) return res.status(400).json({ error: "Path required" });

    const fullPath = safeJoin(WORKSPACE_DIR, folderPath);

    if (fs.existsSync(fullPath)) {
      return res.status(400).json({ error: "Folder already exists" });
    }

    fs.mkdirSync(fullPath, { recursive: true });

    res.json({ message: "Folder created" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get current workspace path
app.get("/api/workspace-path", (req, res) => {
  try {
    res.json({ path: WORKSPACE_DIR.replaceAll("\\", "/") });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Change workspace folder (via absolute path or native Windows file selector fallback)
app.post("/api/open-folder", async (req, res) => {
  try {
    const { path: requestedPath } = req.body;

    if (requestedPath) {
      const target = path.resolve(requestedPath);
      if (!fs.existsSync(target)) {
        fs.mkdirSync(target, { recursive: true });
      }
      WORKSPACE_DIR = target;
      console.log("📂 Workspace changed to:", WORKSPACE_DIR);
      return res.json({ path: WORKSPACE_DIR.replaceAll("\\", "/") });
    }

    // Dynamic import for exec inside async route
    const { exec } = await import("child_process");
    const os = await import("os");

    const vbsScript = `
      Set objShell = CreateObject("Shell.Application")
      Set objFolder = objShell.BrowseForFolder(0, "Select Workspace Folder", 0)
      If Not objFolder Is Nothing Then
          WScript.Echo objFolder.Self.Path
      End If
    `;
    const tempVbsPath = path.join(os.tmpdir(), `select_folder_${Date.now()}.vbs`);
    fs.writeFileSync(tempVbsPath, vbsScript, "utf8");

    exec(`cscript.exe //NoLogo "${tempVbsPath}"`, (error, stdout, stderr) => {
      try {
        fs.unlinkSync(tempVbsPath);
      } catch (e) {}
      if (error) {
        console.error("PowerShell dialog error:", error);
        return res.status(500).json({ error: "Failed to open dialog. Please enter path manually." });
      }

      const selectedPath = stdout.trim();
      if (!selectedPath) {
        // User clicked cancel
        return res.json({ cancelled: true });
      }

      try {
        WORKSPACE_DIR = path.resolve(selectedPath);
        console.log("📂 Workspace changed to:", WORKSPACE_DIR);
        res.json({ path: WORKSPACE_DIR.replaceAll("\\", "/") });
      } catch (err) {
        res.status(400).json({ error: err.message });
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* =========================================================
   PROJECT ZIP DOWNLOAD
   ========================================================= */
app.get("/api/project/download", (req, res) => {
  try {
    res.setHeader("Content-Type", "application/zip");
    res.setHeader(
      "Content-Disposition",
      "attachment; filename=apcre-project.zip",
    );

    const archive = archiver("zip", { zlib: { level: 9 } });

    archive.on("error", (err) => {
      res.status(500).send({ error: err.message });
    });

    archive.pipe(res);

    archive.directory(WORKSPACE_DIR, false);

    archive.finalize();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* =========================================================
   PROJECT ZIP UPLOAD
   ========================================================= */
const zipUpload = multer({ dest: path.join(__dirname, "tmp") });

app.post("/api/project/upload", zipUpload.single("zip"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: "No ZIP uploaded" });

    const zipPath = req.file.path;

    fs.createReadStream(zipPath)
      .pipe(unzipper.Extract({ path: WORKSPACE_DIR }))
      .on("close", () => {
        fs.unlinkSync(zipPath);
        res.json({ message: "ZIP uploaded & extracted successfully" });
      })
      .on("error", (err) => {
        res.status(500).json({ error: err.message });
      });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* =========================================================
   Run Python Code
   ========================================================= */
/* =========================================================
   Run Python Code (UPDATED WITH MULTI-INPUT SUPPORT)
   ========================================================= */
app.post("/api/run", (req, res) => {
  const { filename, code, input } = req.body;

  if (!code) {
    return res.json({
      filename,
      stdout: "",
      stderr: "No code received",
      exitCode: 1,
    });
  }

  const pythonPath = process.env.PYTHON_PATH || "python";

  // 🔥 FIX 1: unbuffered mode
  const py = spawn(pythonPath, ["-u", "-"]);

  let stdout = "";
  let stderr = "";

  py.stdout.on("data", (data) => {
    stdout += data.toString();
  });

  py.stderr.on("data", (data) => {
    stderr += data.toString();
  });

  py.on("close", (exitCode) => {
    res.json({
      filename,
      stdout,
      stderr,
      exitCode,
    });
  });

  // send code first
  py.stdin.write(code + "\n");

  // 🔥 FIX 2: delay input
  setTimeout(() => {
    if (input) {
      py.stdin.write(input + "\n");
    }
    py.stdin.end();
  }, 100);
});

/* =========================================================
   Terminal Commands
   ========================================================= */
app.post("/api/terminal", (req, res) => {
  const { command } = req.body;

  if (!command) return res.json({ output: "No command entered." });

  const cmd = spawn("cmd.exe", ["/c", command], {
    cwd: WORKSPACE_DIR,
  });

  let output = "";

  cmd.stdout.on("data", (data) => (output += data.toString()));
  cmd.stderr.on("data", (data) => (output += data.toString()));

  cmd.on("close", () => {
    res.json({ output: output || "(no output)" });
  });
});

app.get("/api/ml/metrics", async (req, res) => {
  try {
    const response = await fetch(`${AI_ENGINE_URL}/api/ml/metrics`);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   AI Review (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/review", async (req, res) => {
  try {
    const { filename, code } = req.body;
    if (!code) return res.status(400).json({ error: "No code provided" });

    const response = await fetch(`${AI_ENGINE_URL}/api/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, filename }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   FIX API (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/fix", async (req, res) => {
  try {
    const { filename, code, issue } = req.body;
    if (!code) return res.status(400).json({ error: "No code provided" });
    if (!issue?.title) return res.status(400).json({ error: "No issue provided" });

    const response = await fetch(`${AI_ENGINE_URL}/api/fix`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, filename, issue }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   AI Autocomplete (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/generate", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) return res.status(400).json({ error: "No prompt provided" });

    const response = await fetch(`${AI_ENGINE_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
    AI Assistant (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/assistant", async (req, res) => {
  try {
    const { message, filename, code, roomId } = req.body;

    if (!message || !message.trim()) {
      return res.status(400).json({ error: "Message is required" });
    }

    const response = await fetch(`${AI_ENGINE_URL}/api/assistant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, filename, code, roomId }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   Autonomous Coder Agent API (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/agent/automate", async (req, res) => {
  try {
    const { prompt, code, filename } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: "No prompt provided" });
    }

    const response = await fetch(`${AI_ENGINE_URL}/api/agent/automate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, code, filename, workspace_dir: WORKSPACE_DIR }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   Architecture Recommendation Engine API (proxied to Flask AI Engine)
   ========================================================= */
app.post("/api/architecture/recommend", async (req, res) => {
  try {
    const { workspace_dir } = req.body;
    const response = await fetch(`${AI_ENGINE_URL}/api/architecture/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workspace_dir: workspace_dir || WORKSPACE_DIR }),
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "AI Engine not running. Start the Python server on port 5001." });
  }
});

/* =========================================================
   SaaS Pro Upgrade API
   ========================================================= */
app.post("/api/user/upgrade", (req, res) => {
  try {
    const { userId, plan } = req.body;
    if (!userId || !plan) {
      return res.status(400).json({ error: "userId and plan are required." });
    }

    let users = getUsers();
    let index = users.findIndex(u => u.id === userId);
    if (index !== -1) {
      users[index].plan = plan;
      saveUsers(users);
      const userResponse = { ...users[index] };
      delete userResponse.password;
      res.json({ success: true, user: userResponse });
    } else {
      res.status(404).json({ error: "User not found" });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* =========================================================
   Start server (IMPORTANT CHANGE)
   ========================================================= */
server.listen(5000, "0.0.0.0", () => {
  console.log(" APCRE Backend running at http://localhost:5000");
});
