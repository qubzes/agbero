import { useState, useEffect, useRef } from "react";
import { VStack, Container, Box } from "@chakra-ui/react";
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

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

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

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    <Box
      height="100vh"
      width="100%"
      display="flex"
      flexDirection="column"
      position="fixed"
      top={0}
      left={0}
    >
      <Box
        flex={1}
        width="100%"
        overflowY="auto"
        display="flex"
        flexDirection="column"
        alignItems="center"
        mt={[16, 20]}
        mb={[36, 24]}
      >
        <Container maxW="container.lg" height="100%">
          <VStack
            gap={4}
            width={["100%", "100%", "80%"]}
            margin="0 auto"
            mb={20}
          >
            {messages.map((msg, index) => (
              <MessageBubble
                key={index}
                message={msg.content}
                isUser={msg.sender === "user"}
              />
            ))}
            <div ref={messagesEndRef} />
          </VStack>
        </Container>
      </Box>
      <Container maxW="container.lg">
        <ChatInput onSendMessage={addMessage} />
      </Container>
      <Toaster />
    </Box>
  );
};

export default Chat;
