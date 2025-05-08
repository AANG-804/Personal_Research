"use client";
import { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";
import { Switch } from "@/components/ui/switch";

const MODELS = [
  { label: "GPT-4o", value: "gpt-4o" },
  { label: "GPT-4 Turbo", value: "gpt-4-turbo" },
  { label: "GPT-4", value: "gpt-4" },
  { label: "GPT-3.5 Turbo", value: "gpt-3.5-turbo" },
  { label: "Claude 3 Opus", value: "claude-3-opus" },
  { label: "Claude 3 Sonnet", value: "claude-3-sonnet" },
  { label: "Claude 3 Haiku", value: "claude-3-haiku" },
  { label: "Command-R Plus", value: "command-r-plus" },
  { label: "Command-R", value: "command-r" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface Message {
  role: string;
  content: string;
  toolUsed?: string;
  toolInput?: string;
  toolOutput?: string;
}

export default function Home() {
  const [model, setModel] = useState(MODELS[0].value);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [agentMode, setAgentMode] = useState(false);
  const [currentTool, setCurrentTool] = useState<string | null>(null);

  const handleReset = () => {
    setMessages([]);
    setModel(MODELS[0].value);
    setInput("");
    setError(null);
    setAgentMode(false);
    setCurrentTool(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setCurrentTool(null);
    
    // Add user message immediately
    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    
    // Add empty assistant message that will be updated
    setMessages(prev => [...prev, { role: "assistant", content: "" }]);
    
    // Clear input after adding to messages
    setInput("");

    try {
      const endpoint = agentMode ? `${API_URL}/agent/stream` : `${API_URL}/chat/stream`;
      const body = agentMode 
        ? { prompt: input }
        : { prompt: input, model, messages };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get response");
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedResponse = "";
      let toolInfo: { name: string; input: string; output: string } | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        
        // Check for tool usage indicators in the response
        if (text.includes("Using tool:")) {
          const toolMatch = text.match(/Using tool: (.*?)(?:\n|$)/);
          if (toolMatch) {
            setCurrentTool(toolMatch[1]);
            toolInfo = { name: toolMatch[1], input: "", output: "" };
          }
        } else if (text.includes("Tool input:")) {
          const inputMatch = text.match(/Tool input: (.*?)(?:\n|$)/);
          if (inputMatch && toolInfo) {
            toolInfo.input = inputMatch[1];
          }
        } else if (text.includes("Tool output:")) {
          const outputMatch = text.match(/Tool output: (.*?)(?:\n|$)/);
          if (outputMatch && toolInfo) {
            toolInfo.output = outputMatch[1];
            // Update the message with tool information
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage.role === "assistant") {
                lastMessage.toolUsed = toolInfo?.name;
                lastMessage.toolInput = toolInfo?.input;
                lastMessage.toolOutput = toolInfo?.output;
              }
              return newMessages;
            });
            toolInfo = null;
            setCurrentTool(null);
          }
        }

        accumulatedResponse += text;
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = { 
            role: "assistant", 
            content: accumulatedResponse,
            ...(toolInfo && {
              toolUsed: toolInfo.name,
              toolInput: toolInfo.input,
              toolOutput: toolInfo.output
            })
          };
          return newMessages;
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
      setCurrentTool(null);
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading && input.trim()) {
        handleSubmit(e);
      }
    }
  };

  return (
    <div className="max-w-xl mx-auto py-10 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold mb-2">LLM Chat UI</h1>
        <Button 
          variant="outline" 
          onClick={handleReset}
          className="flex items-center gap-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
          Reset
        </Button>
      </div>
      <div className="flex gap-2 items-center">
        <span className="font-medium">Model:</span>
        <Select value={model} onValueChange={setModel} disabled={agentMode}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Select a model..." />
          </SelectTrigger>
          <SelectContent>
            {MODELS.map((m) => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex items-center gap-2 ml-4">
          <Switch checked={agentMode} onCheckedChange={setAgentMode} id="agent-mode" />
          <label htmlFor="agent-mode" className="text-sm select-none cursor-pointer">
            Agent Mode
          </label>
        </div>
      </div>
      {agentMode && (
        <div className="text-xs text-blue-600 dark:text-blue-400 mb-2">
          Agent Mode: Reasoning and tool use enabled (search, etc.)
          {currentTool && (
            <div className="mt-1 flex items-center gap-2">
              <Loader2 className="animate-spin w-3 h-3" />
              <span>Using tool: {currentTool}</span>
            </div>
          )}
        </div>
      )}
      <Card className="min-h-[300px] max-h-[400px] overflow-y-auto p-4 flex flex-col gap-2 bg-muted border shadow-sm">
        {messages.length === 0 && <div className="text-muted-foreground">No messages yet.</div>}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={
              msg.role === "user"
                ? "flex justify-end"
                : "flex justify-start"
            }
          >
            <div
              className={
                msg.role === "user"
                  ? "bg-primary text-primary-foreground rounded-lg px-3 py-2 max-w-[80%]"
                  : "bg-white dark:bg-zinc-900 border rounded-lg px-3 py-2 max-w-[80%] whitespace-pre-line"
              }
            >
              <span className="block text-xs mb-1 opacity-60">
                {msg.role === "user" ? "You" : agentMode ? "Agent" : "AI"}
              </span>
              {msg.content}
              {msg.toolUsed && (
                <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    <span className="font-medium">Tool used:</span> {msg.toolUsed}
                  </div>
                  {msg.toolInput && (
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      <span className="font-medium">Input:</span> {msg.toolInput}
                    </div>
                  )}
                  {msg.toolOutput && (
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      <span className="font-medium">Output:</span> {msg.toolOutput}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-center py-2">
            <Loader2 className="animate-spin w-5 h-5 text-muted-foreground" />
          </div>
        )}
        <div ref={messagesEndRef} />
      </Card>
      <Separator className="my-2" />
      <div className="flex flex-col gap-2">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
          rows={3}
          disabled={loading}
          className="resize-none min-h-[80px]"
        />
        <div className="flex gap-2 items-center">
          <Button onClick={handleSubmit} disabled={loading || !input.trim()}>
            {loading ? (
              <span className="flex items-center gap-2"><Loader2 className="animate-spin w-4 h-4" /> Sending...</span>
            ) : (
              "Send"
            )}
          </Button>
          {error && <span className="text-destructive text-sm">{error}</span>}
        </div>
      </div>
    </div>
  );
}
