import { Box, Text } from "@chakra-ui/react";

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
}

const MessageBubble = ({ message, isUser }: MessageBubbleProps) => (
  <Box
    maxWidth="80%"
    alignSelf={isUser ? "flex-end" : "flex-start"}
    bg={isUser ? "gray.800" : "gray.700"}
    p={2.5}
    borderRadius="xl"
    mb={1}
  >
    <Text fontSize="sm">{message}</Text>
  </Box>
);

export default MessageBubble;
