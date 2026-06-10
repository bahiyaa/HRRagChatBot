import React, { useState } from "react";
import axios from "axios";
import ChatWindow from "./components/ChatWindow";

const App = () => {
  const [messages, setMessages] = useState([
    {
      type: "bot",
      text: "Welcome to NovaTech Knowledge Assistant \n\nI can answer questions based on NovaTech documents and provide relevant source references.\n\nHow may I assist you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    const userMessage = {
      type: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    const question = input;

    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/chat",
        {
          question,
        }
      );
      console.log(response.data);
  
      const botMessage = {
         type: "bot",
         text: response.data.answer,
         sources: response.data.sources,
       };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Error connecting to backend.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <div className="chatbot-popup">
        <div className="chat-header">
          <div className="header-info">
            <ChatWindow />
            <h2 className="logo-text">RAG Assistant</h2>
          </div>
        </div>

        <div className="chat-body">

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${
                msg.type === "bot"
                  ? "bot-message"
                  : "user-message"
              }`}
            >
              {msg.type === "bot" && <ChatWindow />}

              <div>
                <p className="message-text">
                  {msg.text}
                </p>
                
                {msg.sources &&
                  msg.sources.length > 0 && (
                    <div className="sources">
                      {msg.sources.map(
                        (source, i) => (
                          <div
                            key={i}
                            className="source-item"
                          >
                            📄 {source.file}
                            {" "}
                            (Page {source.page})
                          </div>
                        )
                      )}
                    </div>
                  )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message bot-message">
              <p className="message-text">
                Thinking...
              </p>
            </div>
          )}
        </div>

        <div className="chat-footer">
          <form
            className="chat-form"
            onSubmit={sendMessage}
          >
            <input
              type="text"
              placeholder="Ask a question..."
              className="message-input"
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              required
            />

            <button
              type="submit"
              className="material-symbols-rounded"
            >
              arrow_upward
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default App;



// import React from 'react'
// import ChatWindow from './components/ChatWindow'

// const App = () => {
//   return (
//     <div className='container'>
//       <div className='chatbot-popup'>
//          {/* chatbot header */}
       
//         <div className='chat-header'>
//           <div className='header-info'>
//             <ChatWindow></ChatWindow>
//             <h2 className='logo-text'>Chatbot</h2>
//           </div>
//           <button className="material-symbols-rounded">keyboard_arrow_down</button>
//         </div>
//         {/* chatbot body */}
//         <div className='chat-body'>
//           <div className="message bot-message">
//             <ChatWindow></ChatWindow>
//             <p className="message-text">
//               Hey There!<br></br> How can I help you Today?
//             </p>
//           </div>

         
//           <div className="message user-message">
//             <p className="message-text">
//               Loreal ipsum
//             </p>
//           </div>
//         </div>
//         {/* chatbot footer */}
//         <div className="chat-footer">
//           <form action="#" className="chat-form">
//             <input type="text" placeholder='message...' className="message-input" required />
//             <button className="material-symbols-rounded">arrow_upward</button>
//           </form>
//         </div>
//       </div>
//     </div>
//   )
// }

// export default App

