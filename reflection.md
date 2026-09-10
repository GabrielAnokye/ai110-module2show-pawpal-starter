# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

These are the three things a user must be able to do for PawPal+ to be useful.

1. **Set up a pet profile.** The user enters their own name plus the pet's name and species, and any
   preferences that shape care (for example, "no walks after dark" or "meds must come before
   breakfast"). This gives the system someone to plan *for*, and everything else in the app depends
   on it existing first. Without a pet on file, there is nothing to schedule against.

2. **Add and manage care tasks.** The user records the things that need to happen in a day — a walk,
   feeding, medication, grooming, enrichment — and for each one says how long it takes and how
   important it is. They can also edit a task or remove one that no longer applies. This is the raw
   material the scheduler works from: a task the user never entered can never be planned, and a task
   with the wrong duration or priority will quietly distort the whole day.

3. **Generate and read today's plan.** The user says how much time they realistically have, asks
   PawPal+ to build a plan, and gets back an ordered list of tasks with start times that fit inside
   that window. The plan should also say *why* it looks the way it does — which tasks were prioritized,
   and which ones were pushed out because the time ran short. This is the payoff action: the first two
   exist to make this one possible, and the explanation is what makes the user trust the result rather
   than just seeing a list.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
