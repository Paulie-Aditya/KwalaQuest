User performs on-chain action → Kwala detects it → triggers webhook → backend updates user XP → Discord bot announces reward

| Milestone                     | Kwala Trigger        | Bot Reward            |
| ----------------------------- | -------------------- | --------------------- |
| 1st transaction on chain      | ERC-20 Transfer      | “Newbie Trader” badge |
| 10 transactions of same token | Transfer event count | Level up + XP         |
| Holds > 1000 of token X       | Balance > threshold  | Rare “Whale” role     |
| Signs up through bot          | `/register` command  | On-chain address bind |
