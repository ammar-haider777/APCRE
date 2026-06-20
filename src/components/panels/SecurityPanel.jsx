import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, AlertCircle, Terminal, HelpCircle, FileText } from "lucide-react";

export default function SecurityPanel({ selectedFile, issues }) {
  // Map static list of high-value mock OWASP findings to display CWE profiles cleanly
  const mockSecurityIssues = [
    {
      cwe: "CWE-89: SQL Injection via string formatting",
      owasp: "A03:2021-Injection",
      severity: "HIGH",
      badgeColor: "bg-rose-500/10 border-rose-500/20 text-rose-400",
      file: selectedFile ? selectedFile.name : "sql_injection_vuln.py",
      mitigation: "Use parameterized cursor executions or bindings: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
    },
    {
      cwe: "CWE-78: OS Command Injection via shell=True",
      owasp: "A03:2021-Injection",
      severity: "HIGH",
      badgeColor: "bg-rose-500/10 border-rose-500/20 text-rose-400",
      file: selectedFile ? selectedFile.name : "shell_injection.py",
      mitigation: "Avoid shell=True. Pass argument arrays list directly to subprocess: subprocess.run(['ls', '-la'])"
    },
    {
      cwe: "CWE-798: Use of Hardcoded Credentials",
      owasp: "A07:2021-Identification & Auth Failures",
      severity: "HIGH",
      badgeColor: "bg-rose-500/10 border-rose-500/20 text-rose-400",
      file: selectedFile ? selectedFile.name : "hardcoded_creds.py",
      mitigation: "Extract credentials and tokens to secure local environment configurations: os.getenv('APCRE_SECRET')"
    },
    {
      cwe: "CWE-502: Insecure Deserialization via pickle",
      owasp: "A08:2021-Software and Data Integrity Failures",
      severity: "MEDIUM",
      badgeColor: "bg-amber-500/10 border-amber-500/20 text-amber-400",
      file: selectedFile ? selectedFile.name : "insecure_deser.py",
      mitigation: "Avoid deserializing untrusted raw buffers. Use secure schemas: json.loads()"
    }
  ];

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
            <ShieldCheck className="h-6 w-6 text-emerald-500" />
            <span>Security Center (OWASP & CWE)</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Dedicated repository scanner for security vulnerabilities, secrets, and injection threats.</p>
        </div>
      </div>

      {/* 2. OWASP Top 10 Severity Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-md flex items-start gap-4">
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <AlertCircle className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono tracking-wider">Critical OWASP Breaches</div>
            <div className="text-2xl font-bold text-white mt-1 font-mono">3 Active</div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-md flex items-start gap-4">
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Terminal className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono tracking-wider">CWE Vulnerability Types</div>
            <div className="text-2xl font-bold text-white mt-1 font-mono">4 Mapped</div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-md flex items-start gap-4">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono tracking-wider">Ecosystem Status</div>
            <div className="text-2xl font-bold text-white mt-1 font-mono">AUDITED</div>
          </div>
        </div>
      </div>

      {/* 3. Vulnerability Mapping Table */}
      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
          <FileText className="h-4 w-4 text-blue-400" />
          <span>Vulnerabilities Registry</span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono">
                <th className="py-3 px-4">CWE ID & Description</th>
                <th className="py-3 px-4">OWASP Category</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Affected File</th>
                <th className="py-3 px-4">Mitigation Proposal</th>
              </tr>
            </thead>
            <tbody>
              {mockSecurityIssues.map((issue, idx) => (
                <tr key={idx} className="border-b border-slate-850 hover:bg-slate-900/30 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-slate-200">{issue.cwe}</td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono">{issue.owasp}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 border text-[9px] font-bold rounded-full uppercase ${issue.badgeColor}`}>
                      {issue.severity}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-400 truncate max-w-[120px]">{issue.file}</td>
                  <td className="py-3.5 px-4 text-slate-400 leading-normal max-w-[280px]">
                    <div className="bg-slate-950/40 border border-slate-800 p-2 rounded-xl text-[10px] font-mono select-all">
                      {issue.mitigation}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
