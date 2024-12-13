import { Flex, Text } from "@chakra-ui/react";
import { Avatar } from "../ui/avatar";
import { Link } from 'react-router-dom';

const Header = () => (
  <Flex
    p={{base: 2, md: 4}}
    width="100%"
    justifyContent={{
      base: "center",
      md: "flex-start",
    }}
    alignItems="center"
    gap={2}
    position="fixed"
    zIndex="100"
    backgroundColor="#000"
  >
    <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
      <Avatar src="/agbero.png" size="md" />
      <Text fontSize="lg" fontWeight="semibold">
        Agbero Bot
      </Text>
    </Link>
  </Flex>
);

export default Header;
