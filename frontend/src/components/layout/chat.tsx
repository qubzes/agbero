import React, { useState, useEffect } from "react";
import { VStack, Container } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import MessageBubble from "./message-bubble";
import ChatInput from "./chat-input";
import { chat } from "@/api/chat";
import { Message } from "@/types/chat";
import { Toaster, toaster } from "@/components/ui/toaster";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const chatId = window.location.pathname.slice(1);
  const navigate = useNavigate();

  useEffect(() => {
    const initializeChat = async () => {
      try {
        if (!chatId) {
          const newChat = await chat.startNewChat();
          navigate(`/${newChat.chat_id}`);
        } else {
          const existingChat = await chat.getChat(chatId);
          setMessages(existingChat.messages);
        }
      } catch {
        toaster.create({
          description: "Talk no gree load, we don knack fresh mata...",
          type: "error",
        });
        const newChat = await chat.startNewChat();
        navigate(`/${newChat.chat_id}`);
      }
    };

    initializeChat();
  }, [chatId, navigate]);

  const addMessage = async (text: string) => {
    const userMessage: Message = {
      message_id: Date.now().toString(),
      sender: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      const response = await chat.sendMessage(chatId, text);
      const assistantMessage: Message = {
        message_id: response.message_id,
        sender: response.sender,
        content: response.content,
        created_at: response.created_at,
      };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  return (
    <Container
      height="100%"
      width="100%"
      display="flex"
      flexDirection="column"
      alignItems="center"
      maxH="100%"
    >
      <VStack flex={1} overflowY="auto" width={["100%", "80%"]}>
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            message={msg.content}
            isUser={msg.sender === "user"}
          />
        ))}
      </VStack>
      <ChatInput onSendMessage={addMessage} />
      <Toaster />
    </Container>
  );
};

export default Chat;
