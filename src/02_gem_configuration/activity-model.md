# **Template for Educational Coding Activities**

This model breaks down an activity into fundamental sections, each with a specific purpose. Following this structure will help you create comprehensive, engaging, and consistent learning experiences for students.

### **1\. Header and Metadata**

*Every activity should begin with clear metadata that defines its identity and goals at a glance.*

* **Activity Title:** Keep it short, creative, and action-oriented. (e.g., "Build a Smart Traffic Light," "The Two-Key Safe Box.")  
* **Level:** Indicate the complexity (e.g., 1, 2, 3\) to help teachers and students find the right path.  
* **Short Description:** An engaging sentence that summarizes the core challenge and learning outcome. (e.g., "Learn how to use infinite loops to automate a classic traffic light sequence.")  
* **Computational Topics:** List the specific programming concepts that will be covered. (e.g., Variables & Data, Loops, Conditionals & Logic, Sensors & Input.)  
* **General Topics:** Connect the activity to broader curriculum subjects or areas of interest. (e.g., Everyday Life, Art & Music, Mathematics & Logic.)  
* **Tags:** Add keywords to facilitate searching and categorization. (e.g., Loop, Variables, Events, Sensors, Game.)

### **2\. Introduction (The "Hook")**

**Purpose:** To capture the student's interest by connecting the concept to a real-world experience or an intriguing question.

* **Start with a Question or Familiar Context:** Begin with something the student knows. (e.g., "Ever seen the flashing lights on an emergency vehicle?", "Ever wondered how a game keeps score?")  
* **Present a Challenge or a Problem:** Highlight an issue that coding can solve. This creates the need to learn the new concept. (e.g., "Coding a traffic light for a whole day by copying and pasting commands would result in a program millions of lines long\!")  
* **Reveal the "Magic":** Introduce the programming concept as the secret solution to the problem. (e.g., "In this mission, you'll learn the programmer's secret to automation: the infinite loop.")

\[Immagine di uno studente che guarda pensieroso uno schermo di computer\]

### **3\. Teacher's Guide**

**Purpose:** To provide the educator with all the tools needed to facilitate the lesson successfully.

* **Educational Objectives:** List 3-5 clear and measurable learning goals. Use action verbs. (e.g., "Understand the concept of...", "Create a technological object (prototype)...", "Identify relationships between technology and the surrounding world.")  
* **Materials:** List everything required. (e.g., "Cellphone, tablet, or computer; Internet connection.")  
* **Lesson Plan (3-Phase Structure):**  
  1. **Start (10 min \- *The Problem*):** Introduce the activity and pose a challenge that sets the stage for the new concept. (e.g., "How do we make a traffic light run all day? Copying and pasting is impossible\!").  
  2. **Development (20-30 min \- *The Build*):** This is the hands-on phase where the teacher guides students through the "Creation Steps."  
  3. **Closure (5-10 min \- *The Connection*):** Lead a discussion that connects the prototype to the real world, explores its applications, and discusses its limitations. Always end with an extension question or a challenge.

### **4\. Learning Concepts (The Simplified Theory)**

**Purpose:** To explain technical concepts simply, using analogies and a "Problem/Solution" format.

* **Use a Q\&A Format:** Anticipate the student's questions. (e.g., "What is an LED?", "How do devices produce sound?").  
* **Explain the "Why" Before the "How":** Present a concrete problem to demonstrate the need for the new concept.  
  * **The Problem:** "If you tell your prototype to turn a lamp ON and then immediately OFF, you'd see nothing\!"  
  * **The Solution:** "This action of pausing is called Timing."  
* **Leverage Analogies:** Translate abstract concepts into concrete images. (e.g., A **variable** is like a "labeled box where you can store information.")

### **5\. Creation Steps (The Guided Practice)**

**Purpose:** To provide clear and concise instructions for building the project.

* **Device Setup:** List the virtual components (e.g., light sensor, inclination sensor, lamp, etc) to add and how to connect them.  
* **Code Composition:** Do not provide a full "copy-paste" solution. Instead, describe the logic of the construction.  
  * **Pseudocode:** Write a simple, text-based outline of the program's logic. This acts as a language-agnostic guide.  
    * *Example for a Flashing Beacon:*  
      START PROGRAM  
        LOOP forever  
          Turn lamp ON  
          Wait 1 second  
          Turn lamp OFF  
          Wait 1 second  
        END LOOP  
      END PROGRAM

  * **Main Structure:** Describe the overall architecture. (e.g., "Place this entire sequence inside a 'repeat forever' block.")  
  * **Block Locations:** Point out where to find key blocks. (e.g., "The 'repeat forever' block is located in the 'Basic' category.")  
  * **Key Logic:** Explain the critical part of the code. (e.g., "For the condition of the 'if' block, check if the sensor value is greater than a threshold.")

\[Immagine di blocchi di programmazione colorati che vengono assemblati\]

### **6\. Reflection (The Extension of Learning)**

**Purpose:** To encourage critical thinking, creativity, and autonomous application of the learned concepts.

* **Ask Open-Ended Questions:** Prompt reflection on the applications, limitations, or possible variations of the project. (e.g., "What are its weaknesses?", "What is the main difference between a 'for' loop and a 'while' loop?").  
* **Provide a Modification Challenge:** Give a concrete idea for extending the project. This promotes active learning.  
  * **Challenge:** "Add a second button that decreases the count by one."  
  * **Hint:** Offer a small tip to guide the student. (e.g., "You'll need the 'AudioPlayer' component. Where in your IF/ELSE block would you put the 'play sound' and 'stop sound' commands?").