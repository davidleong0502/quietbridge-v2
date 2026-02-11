
[README.md](https://github.com/user-attachments/files/25231655/README.md)
# QuietBridge

QuietBridge is a low-pressure social platform designed to reduce isolation through emotionally sustainable connection.

Instead of optimizing for engagement, it uses:
- A visual daily mood check-in system
- A gentle streak system + coin economy
- Anonymous chatroom
- A reputation-based support board
- Multiplayer connection without emotional labor (Connect Four)
- Private reflection tools

## Summary 

QuietBridge is a gentle, data-driven, community-centered platform designed for people who are too tired for traditional social media but still seek connection. Instead of rewarding constant engagement, fast responses, or curated identities, QuietBridge prioritizes emotional sustainability and psychological safety.

Users check in through a simple visual mood grid, build gentle streaks that encourage consistency without pressure, and use earned coins to participate in a thoughtfully structured community space. Anonymous chats, a reputation-based support board, multiplayer Connect Four, and private reflection tools allow connection with or without conversation. Silence is valid. Lurking is valid. Just showing up is enough.

The platform uses data to foster self-awareness and elevate genuinely helpful contributors, not maximize screen time. Mood analytics, streak tracking, and reputation systems exist to support users, not manipulate them. By combining lightweight interaction, intentional friction, and private reflection, QuietBridge transforms isolation into sustainable connection.

---

## The Problem

**Hackathon Challenge: How can data-driven, community-centered technologies reduce isolation and foster meaningful social engagement?**

Here's what we noticed: loneliness isn't always about being alone. A lot of people are on social media constantly but still feel disconnected. The problem isn't lack of platforms, it's that participating feels exhausting. 

Traditional social media rewards constant engagement, fast responses, perfect posts. If you're already tired, anxious, or going through something difficult, these platforms become impossible to use. You end up withdrawing completely because the cost of showing up feels too high.

We wanted to build something different. Something that recognizes when you're struggling is exactly when you need connection the most, but also when traditional platforms fail you.

---

## Our Solution

QuietBridge is about presence, not performance. You can be here without explaining yourself, without posting the perfect thing, without even talking if you don't want to. The platform works on a simple idea: sometimes just showing up is enough.

Here's what we learned building this:

1. Being tired is a real barrier to connection (not laziness, not antisocial behavior)
2. You can feel less alone just by being in a space with others, even silently
3. Small, easy actions keep people engaged when big commitments would push them away
4. Anonymous identities remove the pressure to perform or impress
5. Data should help you understand yourself, not optimize your engagement for the platform's benefit

---

## What It Does

### Visual Mood Check-In

Instead of typing out how you feel (which can be really hard when you're not doing well), you just tap a word on a 4x4 grid. The grid is based on the circumplex model of affect, basically mapping emotions by energy level and pleasantness.

So you might tap "Tired" in the bottom left, or "Calm" in the middle, or "Excited" in the top right. That's it. No explanation needed. The system tracks these over time so you can see patterns you might not notice daily.

### Streak System with Coins

Every day you check in, you earn coins based on your streak:
- 1 day: +1 coin
- 3 days: +2 coins  
- 5+ days: +3 coins

There's a "gentle mode" that gives you a 1-day grace period, because life happens. The coins aren't just arbitrary, you use them to participate in the community (more on that below).

You also get a calendar heatmap showing 16 weeks of check-ins. It's like GitHub's contribution graph but for your emotional consistency. Darker colors mean higher mood levels. You can literally see at a glance whether you've been checking in, and what your general patterns look like.

### Chatroom

This is just a simple chat space. Last 20 messages show up. No likes, no reactions, no read receipts, no follower counts. Your name is something auto generated like "CalmRiver" or "WarmFox" so there's no identity pressure.

Messages here are short and gentle. People say stuff like "anyone else exhausted today?" and others respond with "yeah, same" or "it's okay to just be." That's the vibe. Low stakes, low pressure.

### Community Query Board

This is where the coin system gets interesting. Posting a question costs 10 coins. Replying costs 2 coins. Every reply you write earns you +1 reputation.

The cost creates friction (in a good way). It means people don't spam. They think about what they're posting. And replies are sorted by reputation, so people who consistently give helpful advice naturally rise to the top. The community self moderates through data.

You can post anonymously or with your username. Search works to find past discussions. It's basically a support forum but designed to actually be supportive.

### Connect Four

Sometimes you don't want to talk about feelings at all. Sometimes you just want to do something alongside other people. So we built in multiplayer Connect Four.

You join a lobby, get matched with someone, play a quick game. Winner gets +10 trophies, loser gets -4 (but it never goes below 0). There's a 60 second AFK timer to keep games moving.

The genius here is that it's connection without emotional labor. You're playing with a real person but you don't have to perform or explain anything. Just show up and play.

### Private Reflection

Every day there's a gentle prompt like "What's one small thing you survived today?" You can write as much or as little as you want. Nothing gets saved permanently, it stays in your session only. Nobody else sees it.

This is for the heavy stuff you need to process but aren't ready to share. It's private space within a social platform, which sounds contradictory but actually makes perfect sense when you're building for emotional wellbeing.

### Dashboard  

The dashboard shows you:
- Your most frequent moods over time
- Average mood score (1-4 scale)
- The calendar heatmap we mentioned
- Personalized insights based on your patterns (non-judgmental, like "you've been checking in consistently")

The data here isn't used to make you engage more. It's a mirror. It helps you see patterns you might not notice otherwise. Like realizing you're always "overwhelmed" on Sundays, or that you've been more balanced lately than you thought.

---

## How Users Experience It

When you first open QuietBridge:
- No login, no signup
- You get assigned a name like "CalmRiver"  
- You start with 12 coins, 0 reputation, 0 trophies
- You see 6 pages in the sidebar: Home, Dashboard, Chatroom, Community Query, Connect Four, Reflection

On the Home page, you see the mood grid. You tap how you're feeling. When you save it, the system gives you a gentle suggestion, e.g. "based on how you're feeling, you might want to try the Chatroom." You can follow that suggestion or ignore it.

Below the mood grid is your streak card showing your current streak, best streak, average mood over the last 7 days, and weekly progress. If you just checked in, it shows a green dot and says "Checked in today." There's also a motivational note like "gentle consistency beats perfection."

Go to the Dashboard and you'll see the heatmap, your mood statistics, and recent check-in history with timestamps. It's all there in a clean, non-overwhelming layout.

Chatroom is exactly what it sounds like. You can read messages or send one. The interface shows everyone's reputation and trophy count next to their name, not to create hierarchy, but to give you context about who you're talking to.

Community Query shows the cost/reward system at the top. You can post a new question (expandable section) or scroll through existing posts. Each post shows replies sorted by the author's reputation. Below each post is a reply box where you can add your own response.

Connect Four shows how many people are in the lobby (with little lightbulb icons for each person). Click "Join lobby" and you'll get matched when someone else is available. During the game, you see both players' trophy counts, whose turn it is, the AFK countdown, and the game board. Column buttons below let you make your move.

Reflection is the simplest page. Just the prompt, a text area, and a save button. After saving you see your last few reflections listed.

Here's how the economy works in practice:

Day 1: You open the app, get assigned a name, tap "Tired" on the mood grid, save your check-in. You now have a 1-day streak and earn 1 coin (total: 13 coins). You look at the dashboard, one dot on the heatmap. You read the chatroom, feel a little less alone, don't send anything. You write a private reflection and log off.

Day 3: You come back (because yesterday you checked in too). You tap "Calm" and save. You now have a 3-day streak, so you earn 2 coins (total: 15 coins). Your dashboard shows a nice pattern forming. You post a question to Community Query about something you're struggling with, which costs 10 coins (total: 5 coins). Two people reply with helpful advice. You feel supported. You try Connect Four, lose your first game (-4 trophies), but it was actually fun.

Day 7: You're at a 7-day streak earning 3 coins each day. You've accumulated enough coins to participate actively. Your reputation is at 5 because you've been replying to other people's posts. When you reply now, your comments appear higher up because of your reputation score. You've become a trusted voice in the community just by being consistently helpful. The dashboard shows you've been mostly calm and content this week, with an average mood of 3.2/4.

---

## Design Philosophy

Every design choice was intentional:

**Psychological safety first.** No profiles, no permanent records, no public metrics that could become sources of shame. Everything is optional and reversible.

**Silence is valid.** You can lurk in the chatroom. You can observe the lobby without joining. You can read Community Query posts without replying. Being present is enough.

**Visual over verbal.** The mood grid lets you check in without words. Connect Four lets you connect without talking. We reduced reliance on language because sometimes you just don't have the words.

**Good friction.** The coin system creates intentional slowdown. It's not about restricting access, it's about making people pause and think. Thoughtful participation beats rapid fire posting.

**Ephemeral identity.** Your auto generated name is friendly and random. It's persistent enough that your reputation builds, but detached enough that you're not worried about your personal brand.

**Data for awareness, not manipulation.** The analytics show YOU your patterns. They're not fed into an algorithm to make you engage more. The platform doesn't benefit from your activity, you do.

**Easy exit.** No explanations needed to leave. No guilt. You can come back whenever. The app will be here.

---

## Safety & Ethical Considerations

Because QuietBridge operates in emotionally vulnerable spaces, safety and ethical design were core considerations. QuietBridge is designed for emotional wellbeing, not crisis intervention.

Safeguards include:
- Reputation-weighted replies to elevate consistently helpful users
- Intentional friction (coin costs) to reduce spam and impulsive posting
- No public follower counts or vanity metrics
- No algorithmic feed optimization
- Reflections are session-only and never permanently stored

Future improvements:
- Content moderation filters
- Elected community moderators
- Escalation links to professional resources

---

## Technical Stack

Built with Python and Streamlit. Deployed on Streamlit Cloud.

The architecture separates private data from shared data:

Private (session-level): Your mood history, reflections, check-ins, wallet, reputation, trophies

Shared (server-level): Chat messages, community queries, game lobbies, active matches

When you select a mood, here's what happens:
1. You click "Tired"
2. System maps it to the "Lonely" category (backend uses 4 categories even though users see 16 words)
3. Calculates numeric level (Lonely = 2 out of 4)
4. Recommends Chatroom since that's the best support for that mood
5. Creates a check-in record with date, word, category, level, timestamp
6. Saves to checkins.json
7. Calculates your streak
8. Awards coins based on streak length (once per day)
9. Updates your wallet
10. Dashboard regenerates with the new data point
11. Heatmap gets darker for today
12. You see your coin balance increase in the sidebar

The codebase is split into modules:

app.py handles routing and state management. mood_logic.py maps the 16 words to 4 categories and recommends features. daily.py handles check-in tracking and streak calculations. dashboard.py generates analytics and insights. wallet.py manages the economy (coins, reputation, trophies). game.py runs the Connect Four multiplayer engine. personas.py generates random names.

Data persists in two JSON files: checkins.json stores all your daily check-ins, wallets.json stores everyone's coins/reputation/trophies.

Key decision: Reflections are session-only. They never persist. This is by design, they're meant to be a safe space for processing heavy stuff without worrying it'll be saved forever.

---

## Connecting to the Challenge

We were asked: how can data-driven, community-centered technologies reduce isolation?

Here's how each piece addresses that:

**Data-driven parts:**
- Mood tracking shows emotional patterns over time (users see what they didn't notice)
- Streak system uses data to create gentle accountability
- 7-day analytics provide insight without judgment  
- Reputation system surfaces helpful people through data, not algorithms
- Trophy tracking gamifies connection through measurable progress

**Community-centered parts:**
- Anonymous names remove performance anxiety
- Chatroom validates silent presence (you don't have to participate to belong)
- Community Query structures vulnerability with peer support and incentives
- Connect Four creates connection through play instead of emotional labor
- Private Reflection prevents oversharing while still supporting processing

The magic is how they work together:

You check in daily → earn coins → post to Community Query → get helpful replies (sorted by reputation) → feel supported → reply to others → earn reputation → become a trusted voice → cycle continues. Data and community reinforce each other to transform isolated users into connected members.

The data isn't extractive. It doesn't optimize for engagement. It serves the user's wellbeing. That's the ethical foundation.

---

## Impact

This helps people who are tired, burned out, anxious, depressed, grieving, or just going through something difficult. Traditional social platforms fail them because participation requires energy they don't have. QuietBridge meets them where they are.

Measurable outcomes:
- Check-in streaks indicate consistent self-awareness habits
- Reputation scores show who's genuinely helpful
- Chat participation reveals users choosing connection when ready
- Mood heatmaps inform personal wellbeing decisions
- Trophy counts demonstrate playful engagement

But the real impact is harder to measure: someone staying connected during a rough week instead of withdrawing completely. Someone feeling less alone because they saw others in the chatroom. Someone getting helpful advice that actually helped. Someone building a streak and feeling proud of that consistency.

---

## What's Next

Possible future directions:
- Deploy for specific institutions (schools, workplaces, support groups)
- Add community moderators elected by reputation
- Optional accounts for users who want persistence across sessions
- Integration with mental health resources
- Gentle nudges toward professional support when patterns suggest it

---

## Running It

Live demo: https://quietbridge-v2-gtszsuvtwfggvdaj7yg5fm.streamlit.app/

To run locally:
- Clone the repo
- Install from requirements.txt (streamlit, pandas, altair, pillow, streamlit-image-coordinates)
- Run `streamlit run app.py`
- Open localhost:8501

---

Built for Beyond Binary by Parallax

*Connection doesn't require conversation. Sometimes, just showing up is enough.*
