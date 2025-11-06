User performs on-chain action → Kwala detects it → triggers webhook → backend updates user XP → Discord bot announces reward

| Milestone                     | Kwala Trigger        | Bot Reward            |
| ----------------------------- | -------------------- | --------------------- |
| 1st transaction on chain      | ERC-20 Transfer      | “Newbie Trader” badge |
| 10 transactions of same token | Transfer event count | Level up + XP         |
| Holds > 1000 of token X       | Balance > threshold  | Rare “Whale” role     |
| Signs up through bot          | `/register` command  | On-chain address bind |

| Gamification Feature                  | How it Works                                         |
| ------------------------------------- | ---------------------------------------------------- |
| ✅ XP per transaction                 | +5 XP per token transfer involving registered wallet |
| ✅ Level system                       | Level = floor(xp / 100)                              |
| ✅ Leaderboard command `/leaderboard` | Shows top 10 XP users                                |
| ✅ Roles based on level               | Level 1 = Rookie, Level 5 = Trader, Level 10 = Whale |
| ✅ Badges                             | First Tx, 10 Tx, First 1k balance, etc               |
| ✅ Weekly quests                      | “Do 3 transfers this week → earn bonus XP”           |
| ✅ Streaks                            | 1 transfer per day for 7 days → bonus XP             |
| ✅ Discord UI buttons (optional)      | Claim badge, view stats, etc                         |
