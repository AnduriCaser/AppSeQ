const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");
const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbotCloseBtn = document.querySelector(".close-btn");

let userMessage;
const API_KEY = ""; // OpenAI hesabınızdan alın
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);
  let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;  
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi;
}

const sendPromptToOpenAI = async (prompt) => {
  const API_URL = "https://api.openai.com/v1/engines/text-davinci-003/completions";
  
  const requestOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    }, 
    body: JSON.stringify({
      prompt: prompt,
      max_tokens: 1,
      temperature: 0,
      stop: ["\n"],
    })
  };

  try {
    const response = await fetch(API_URL, requestOptions);
    if (!response.ok) {
      throw new Error("Failed to fetch data from OpenAI API. Status code: " + response.status);
    }
    const data = await response.json();
    return data.choices[0].text.trim();
  } catch (error) {
    console.error("Error:", error.message);
    return null;
  }
}

const handleChat = async () => {
  userMessage = chatInput.value.trim();
  if (!userMessage) return;
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  const isCyberSecurityRelated = await sendPromptToOpenAI(userMessage + "\nIs this related to cyber security?\n");
  
  if (isCyberSecurityRelated === "Yes") {
    chatbox.appendChild(createChatLi("This is related to cyber security.", "incoming"));
  } else if (isCyberSecurityRelated === "No") {
    chatbox.appendChild(createChatLi("This is not related to cyber security.", "incoming"));
  } else {
    chatbox.appendChild(createChatLi("I'm not sure about that.", "incoming"));
  }

  chatbox.scrollTo(0, chatbox.scrollHeight);
}

chatInput.addEventListener("input", () =>{
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;  
});

chatInput.addEventListener("keydown", (e) =>{
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

sendChatBtn.addEventListener("click", handleChat);
chatbotCloseBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
