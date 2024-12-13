import React, { useState } from "react";
import { VStack, Container } from "@chakra-ui/react";
import MessageBubble from "./message-bubble";
import ChatInput from "./chat-input";
import { chatService } from "@/api/chat";
import { useEffect } from "react";
interface Message {
  text: string;
  isUser: boolean;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const initializeChat = async () => {
      try {
        await chatService.startNewChat();
      } catch (error) {
        console.error("Failed to start new chat:", error);
      }
    };

    initializeChat();
  }, []);
  const getDummyResponse = () => {
    const responses = [
      "I understand what you're saying.",
      "That's interesting! Tell me more.",
      "I'm here to help you.",
      "Let me think about that...",
      "Could you elaborate on that?",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const addMessage = (text: string) => {
    const userMessage = { text, isUser: true };
    const assistantMessage = { text: getDummyResponse(), isUser: false };

    setMessages([...messages, userMessage, assistantMessage]);
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
          <MessageBubble key={index} message={msg.text} isUser={msg.isUser} />
        ))}
      </VStack>
      <ChatInput onSendMessage={(text) => addMessage(text)} />
    </Container>
  );
};

export default Chat;
