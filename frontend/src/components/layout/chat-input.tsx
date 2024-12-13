import { Box, Text, Flex, Input } from "@chakra-ui/react";
import { useState } from "react";
import { Button } from "../ui/button";
import { FaFistRaised } from "react-icons/fa";

const ChatInput = ({
  onSendMessage,
}: {
  onSendMessage: (message: string) => void;
}) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const placeholders = [
    "Knack your coded parole here, no dulling!",
    "Yarn wetin dey for your mind—no dey fear!",
    "Drop your rugged message, no loose guard!",
    "Offload your coded tinz here, senior man!",
    "Make your parole land here, no slack!",
    "Knack street-level gist, no dey hide am!",
    "Offload your matter here, no yawa!",
    "Abeg, knack wetin dey sup for your side!",
    "Oya yarn your mind, coded and sharp!",
    "Knack beta gist wey make sense!",
    "Make your rugged vibes enter here sharp!",
    "Yarn your coded tinz here, omo street!",
    "Offload your matter here, steady no slack!",
    "Knack strong talk here—coded levels only!",
    "Yarn coded parole, no dey look face!",
  ];

  return (
    <Box
      width="100%"
      position="fixed"
      bottom={0}
      left={0}
      backgroundColor="#000"
      zIndex="100"
    >
      <Flex
        width={["100%", "100%", "60%"]}
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        margin="0 auto"
        p={2}
      >
        <Box position="relative" width="100%" mx="auto" py={1}>
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleSend();
              }
            }}
            placeholder={
              placeholders[Math.floor(Math.random() * placeholders.length)]
            }
            bg="gray.800"
            border="none"
            borderRadius="2xl"
            p={6}
            pr="3rem"
            pl="1rem"
          />
          <Button
            onClick={handleSend}
            size="sm"
            borderRadius="2xl"
            position="absolute"
            right="0.5rem"
            top="50%"
            transform="translateY(-50%)"
            p={0}
            disabled={!message.trim()}
          >
            <FaFistRaised />
          </Button>
        </Box>
        <Text color="gray.600" fontSize={["xs", "sm"]} textAlign="center">
          Dis bot na for rugged cruise, no use am for gbege or yawa.
        </Text>
      </Flex>
    </Box>
  );
};

export default ChatInput;
