import { HStack, Text } from "@chakra-ui/react";
import { Avatar } from "../ui/avatar";

const Header = () => (
  <HStack
    p={{base: 2, md: 4}}
    width="100%"
    justifyContent={{
      base: "center",
      md: "flex-start",
    }}
  >
    <Avatar src="/agbero.png" size="md" />
    <Text fontSize="lg" fontWeight="semibold">
      Agbero Bot
    </Text>
  </HStack>
);

export default Header;
