// frontend/src/components/ChatWindow.jsx
import { useState, useEffect, useRef } from "react";
import { askQuestion, getHistory, sendFeedback } from "../api.js";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const chatExportRef = useRef(null);

  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadHistory = async () => {
    const history = await getHistory();
    setMessages(history.map(m => ({ ...m, isTyping: false }))); // Fix key warning
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userQuestion = input;
    setInput("");
    setIsTyping(true);

    // Add user message instantly
    setMessages(prev => [...prev, {
      id: Date.now(),
      question: userQuestion,
      response: "AI is typing...",
      isTyping: true,
      priority: "normal",
      category: "",
      sentiment: "neutral"
    }]);

    try {
      await askQuestion(userQuestion);
      setIsTyping(false);
      loadHistory();
    } catch (err) {
      setIsTyping(false);
      alert("Error sending message");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Delete this message permanently?")) {
      await fetch(`http://localhost:5000/delete/${id}`, { method: "DELETE" });
      loadHistory();
    }
  };

  const exportToPDF = async () => {
    if (!chatExportRef.current) return;
    
    const canvas = await html2canvas(chatExportRef.current, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");
    const width = pdf.internal.pageSize.getWidth();
    const height = (canvas.height * width) / canvas.width;

    pdf.addImage(imgData, "PNG", 0, 0, width, height);
    pdf.save("AI-Support-Chat.pdf");
  };

  return (
    <div className={`flex flex-col h-screen transition-all duration-500 ${darkMode ? "bg-gray-900 text-white" : "bg-gradient-to-b from-gray-50 to-gray-100"}`}>
      {/* Header */}
      <div className={`p-6 shadow-2xl flex justify-between items-center ${darkMode ? "bg-gray-800" : "bg-gradient-to-r from-indigo-600 to-purple-700"} text-white`}>
        <div>
          <h2 className="text-3xl font-bold">AI Customer Support</h2>
          <p className="opacity-90">Your Custom Model in Action</p>
        </div>
        <div className="flex gap-4 items-center">
          <button onClick={exportToPDF} className="bg-white text-indigo-700 px-6 py-3 rounded-xl font-bold hover:scale-105 transition shadow-lg">
            Export PDF
          </button>
          <button onClick={() => setDarkMode(!darkMode)} className="text-3xl hover:scale-125 transition">
            {darkMode ? "Sun" : "Moon"}
          </button>
        </div>
      </div>

      {/* Hidden PDF Export Area */}
      <div ref={chatExportRef} className="absolute left-[-9999px] top-0 w-[800px] bg-white text-black p-10">
        <h1 className="text-4xl font-bold text-center mb-8">AI Support Chat Transcript</h1>
        <p className="text-center text-gray-600 mb-8">Generated on {new Date().toLocaleString()}</p>
        {messages.map((m, i) => (
          <div key={i} className="mb-8 border-b pb-6">
            <p className="font-bold text-lg">You: {m.question}</p>
            <p className="text-gray-700 mt-2 text-lg">AI: {m.response}</p>
          </div>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {messages.map((msg, index) => (
          <div
            key={msg.id || index} // Fixed key warning
            className={`group relative p-6 rounded-2xl shadow-lg border-l-8 transition-all ${
              msg.priority === "urgent"
                ? "border-red-600 bg-red-50 animate-pulse"
                : darkMode ? "border-gray-700 bg-gray-800" : "border-indigo-600 bg-white"
            }`}
          >
            {/* Delete Button */}
            <button
              onClick={() => handleDelete(msg.id)}
              className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg"
            >
              Trash
            </button>

            <p className="font-bold text-lg">{msg.question}</p>
            <p className="mt-2 font-medium text-indigo-600 dark:text-indigo-400">{msg.response}</p>

            {/* Model Highlights */}
            <div className="mt-4 flex flex-wrap gap-3">
              {msg.category && (
                <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full shadow-md">
                  Category: {msg.category}
                </span>
              )}
              {msg.priority === "urgent" && (
                <span className="px-4 py-2 bg-red-600 text-white font-bold rounded-full shadow-md animate-pulse">
                  Priority: URGENT
                </span>
              )}
            </div>

            {/* Feedback Buttons — ONLY if no feedback yet */}
            {!msg.feedback && msg.id && (
              <div className="flex gap-4 mt-4">
                <button onClick={() => sendFeedback(msg.id, "positive")} className="text-3xl hover:scale-125 transition">Positive</button>
                <button onClick={() => sendFeedback(msg.id, "negative")} className="text-3xl hover:scale-125 transition">Negative</button>
              </div>
            )}
          </div>
        ))}

        {/* AI Typing */}
        {isTyping && (
          <div className={`flex items-center gap-3 p-5 rounded-2xl w-fit ${darkMode ? "bg-gray-800" : "bg-gray-200"}`}>
            <div className="flex gap-2">
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce"></div>
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce delay-100"></div>
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce delay-200"></div>
            </div>
            <span className="font-medium">AI is typing...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div className={`p-6 ${darkMode ? "bg-gray-800" : "bg-white"} shadow-2xl`}>
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Type your message..."
            className={`flex-1 px-6 py-5 text-lg rounded-2xl focus:outline-none transition ${
              darkMode
                ? "bg-gray-700 text-white placeholder-gray-400"
                : "bg-gray-100 text-gray-800 placeholder-gray-500 border-2 border-transparent focus:border-purple-600"
            }`}
          />
          <button
            onClick={handleSend}
            className="px-10 py-5 bg-gradient-to-r from-indigo-600 to-purple-700 text-white font-bold rounded-2xl hover:shadow-2xl transition transform hover:scale-105"
          >
            Send
          </button>
        </div>
      </div>

    </div>
      
  );
}