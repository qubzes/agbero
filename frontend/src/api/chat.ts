import api from "./client";
import { StartChat, Chat, Message } from "@/types/chat";

export const chat = {
  getAllChats: async (): Promise<StartChat[]> => {
    const response = await api.get<StartChat[]>("/chats");
    return response.data;
  },

  startNewChat: async (): Promise<StartChat> => {
    const response = await api.post<StartChat>("/chats", {});
    return response.data;
  },

  getChat: async (chatId: string): Promise<Chat> => {
    const response = await api.get<Chat>(`/chats/${chatId}`);
    return response.data;
  },

  sendMessage: async (chatId: string, message: string): Promise<Message> => {
    const response = await api.post<Message>(`/chats/${chatId}/message`, {
      message,
    });
    return response.data;
  },
};
