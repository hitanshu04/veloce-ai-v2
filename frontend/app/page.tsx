"use client";
import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import { Loader2, Play, CheckCircle, Send, Bot, User, Sparkles, X, ListChecks } from "lucide-react";

interface Message {
  role: 'user' | 'ai';
  content: string;
}

export default function VeloceHome() {
  // --- STATE MANAGEMENT ---
  const [url, setUrl] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null); // ✨ NEW: Summary State
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // --- AUTO SCROLL ---
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, chatLoading]);

  // --- RESET SESSION ---
  const resetSession = () => {
    setJobId(null);
    setStatus(null);
    setUrl("");
    setMessages([]);
    setQuestion("");
    setLoading(false);
    setSummary(null); // ✨ NEW: Reset Summary
  };

  // --- POLLING LOGIC ---
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (jobId && status?.status !== "completed" && status?.status !== "failed") {
      interval = setInterval(async () => {
        try {
          const data = await api.getStatus(jobId);
          if (!jobId) return; 
          setStatus(data);

          // ✨ NEW: Capture Summary when ready
          if (data.status === "completed" && data.summary) {
            setSummary(data.summary);
          }
        } catch (error) {
          console.error("Polling error", error);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  // --- HANDLERS ---
  const handleProcess = async () => {
    if (!url) return;
    setLoading(true);
    setStatus(null);
    setMessages([]); 
    setSummary(null); // Reset for new process
    try {
      const { job_id } = await api.processVideo(url);
      setJobId(job_id);
    } catch (err) {
      alert("Backend connection failed.");
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!question.trim() || !jobId) return;
    const userMsg = question;
    setQuestion("");
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatLoading(true);

    try {
      const data = await api.chat(jobId, userMsg);
      setMessages(prev => [...prev, { role: 'ai', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "⚠️ Error: AI response failed." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const showChat = status?.status === 'completed';

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center py-6 px-4 font-sans selection:bg-blue-500/30 overflow-hidden">
      
      {/* HEADER */}
      {!showChat && (
        <div className="text-center space-y-4 mb-12 mt-16 animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="inline-flex items-center justify-center p-4 bg-slate-900 rounded-3xl border border-slate-800 shadow-2xl shadow-blue-900/20 mb-2">
              <Sparkles className="text-blue-400 w-8 h-8 animate-pulse" />
          </div>
          <h1 className="text-6xl md:text-8xl font-bold bg-gradient-to-b from-white via-slate-200 to-slate-500 bg-clip-text text-transparent tracking-tighter">
            Veloce-AI
          </h1>
          <p className="text-slate-400 text-xl font-light tracking-wide max-w-lg mx-auto">
            Don't just watch videos. <span className="text-blue-400 font-medium">Chat with them</span>. ✨
          </p>
        </div>
      )}

      {/* INPUT CARD */}
      {!showChat && (
        <div className="w-full max-w-2xl animate-in fade-in zoom-in-95 duration-500">
          <div className="bg-slate-900/60 backdrop-blur-xl p-1.5 rounded-[32px] border border-slate-800 shadow-2xl ring-1 ring-white/5">
            <div className="bg-slate-950/90 rounded-[28px] p-8">
              
              <label className="text-xs font-bold text-blue-500 uppercase tracking-widest ml-2 mb-3 block">
                YouTube Link
              </label>
              
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  placeholder="Paste video URL here..."
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl px-6 py-4 text-lg text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all placeholder:text-slate-600"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleProcess()}
                />
                <button
                  onClick={handleProcess}
                  disabled={loading || !url}
                  className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed px-8 py-4 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-xl shadow-blue-600/20 active:scale-95"
                >
                  {loading ? <Loader2 className="animate-spin w-6 h-6" /> : <Play className="w-6 h-6 fill-current" />}
                  <span>Start</span>
                </button>
              </div>

              {status && (
                <div className="mt-8 pt-6 border-t border-slate-800/50 animate-in fade-in slide-in-from-top-2">
                  <div className="flex justify-between items-center mb-2">
                     <span className="text-sm font-medium text-slate-300 flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                        {status.step || "Processing..."}
                     </span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 w-[70%] animate-pulse rounded-full"></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* CHAT INTERFACE */}
      {showChat && (
        <div className="fixed inset-0 bg-slate-950 z-50 flex flex-col animate-in slide-in-from-bottom-[10%] duration-500">
          
          <div className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-4">
               <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Sparkles className="text-white w-5 h-5" />
               </div>
               <div>
                  <h2 className="font-bold text-white text-lg leading-tight">Video Intelligence</h2>
                  <p className="text-xs text-slate-400 truncate max-w-[200px] md:max-w-md">
                    {status.title || "Ready to assist"}
                  </p>
               </div>
            </div>

            <button onClick={resetSession} className="p-2 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 rounded-full transition-all border border-slate-700 group">
              <X className="w-6 h-6 group-hover:rotate-90 transition-transform" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth bg-gradient-to-b from-slate-950 to-slate-900">
            
            {/* ✨ NEW: AUTO-GENERATED SUMMARY BOX ✨ */}
            {summary && (
              <div className="max-w-4xl mx-auto mb-8 animate-in fade-in zoom-in-95 duration-1000">
                <div className="bg-blue-600/10 border border-blue-500/30 rounded-3xl p-6 md:p-8 backdrop-blur-sm relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    <ListChecks size={80} />
                  </div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                      <Sparkles size={20} />
                    </div>
                    <h3 className="text-xl font-bold text-white">Video Takeaways</h3>
                  </div>
                  <div className="text-slate-200 text-base md:text-lg leading-relaxed whitespace-pre-line border-l-2 border-blue-500/50 pl-4">
                    {summary}
                  </div>
                </div>
              </div>
            )}

            {messages.length === 0 && !summary && (
              <div className="h-full flex flex-col items-center justify-center opacity-40 space-y-4">
                <Bot size={80} strokeWidth={0.5} />
                <p className="text-lg">Ask me anything about the video.</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4`}>
                {msg.role === 'ai' && (
                  <div className="w-8 h-8 bg-slate-800 border border-slate-700 rounded-full flex items-center justify-center flex-shrink-0 mt-2">
                    <Sparkles size={14} className="text-blue-400" />
                  </div>
                )}
                <div className={`max-w-[85%] md:max-w-[70%] p-5 rounded-2xl text-[15px] leading-relaxed shadow-sm ${
                  msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}

            {chatLoading && (
              <div className="flex gap-4">
                  <div className="w-8 h-8 bg-slate-800 border border-slate-700 rounded-full flex items-center justify-center">
                    <Sparkles size={14} className="text-blue-400" />
                  </div>
                  <div className="bg-slate-900 border border-slate-800 px-5 py-4 rounded-2xl rounded-tl-none flex items-center gap-1.5">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-2" />
          </div>

          <div className="p-4 md:p-6 bg-slate-950 border-t border-slate-800">
            <div className="max-w-4xl mx-auto relative flex items-center gap-3">
              <input
                type="text"
                placeholder="Type your question..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-6 pr-16 py-4 text-slate-100 focus:outline-none focus:border-blue-500 transition-all placeholder:text-slate-500 shadow-inner text-base"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
              />
              <button
                onClick={handleChat}
                disabled={chatLoading || !question.trim()}
                className="absolute right-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 p-2.5 rounded-lg transition-all active:scale-95"
              >
                <Send size={20} />
              </button>
            </div>
            <p className="text-center text-[10px] text-slate-600 mt-3 uppercase tracking-widest">
               Veloce-AI Engine v2.0
            </p>
          </div>
        </div>
      )}
    </main>
  );
}