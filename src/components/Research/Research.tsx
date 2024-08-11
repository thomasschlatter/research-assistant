import React, { useState } from "react";

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    []
  );
  const [input, setInput] = useState("");

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    // Add user message to chat
    setMessages([...messages, { role: "user", content: input }]);

    // Send the input to the API
    try {
      const response = await fetch("http://localhost:5000/langchain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: input }),
      });

      const data = await response.json();

      // Add API response to chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "system", content: data.response },
      ]);
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "system", content: "Error: Unable to reach the API." },
      ]);
    }

    // Clear the input field
    setInput("");
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Chat with API</h1>
      <div
        style={{
          border: "1px solid #ccc",
          padding: "10px",
          height: "300px",
          overflowY: "scroll",
          marginBottom: "10px",
        }}
      >
        {messages.map((msg, index) => (
          <div key={index} style={{ margin: "10px 0" }}>
            <strong>{msg.role === "user" ? "You" : "Bot"}:</strong>{" "}
            {msg.content}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        style={{ width: "80%", padding: "10px" }}
        placeholder="Type your message here..."
      />
      <button
        onClick={handleSendMessage}
        style={{ padding: "10px 20px", marginLeft: "10px" }}
      >
        Send
      </button>
    </div>
  );
};

export default ChatWindow;
