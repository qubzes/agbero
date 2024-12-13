import { apiClient } from "./client";

interface Message {
  id: string;
  content: string;
  senderId: string;
  timestamp: Date;
}

interface Chat {
  id: string;
  participants: string[];
  messages: Message[];
  createdAt: Date;
}

export const chatService = {
  getAllChats: async (): Promise<Chat[]> => {
    const response = await apiClient.get<Chat[]>("/chats");
    return response.data;
  },

  startNewChat: async (): Promise<Chat> => {
    const response = await apiClient.post<Chat>("/chats", {});
    return response.data;
  },

  getChat: async (chatId: string): Promise<Chat> => {
    const response = await apiClient.get<Chat>(`/chats/${chatId}`);
    return response.data;
    return response.data;
  },

  sendMessage: async (chatId: string, content: string): Promise<Message> => {
    const response = await apiClient.post<Message>(
      `/chats/${chatId}/messages`,
      {
        content,
      }
    );
    return response.data;
  },
};
