const menuButton = document.querySelector(".menu-toggle");
const nav = document.querySelector(".main-nav");

if (menuButton && nav) {
  menuButton.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });

  nav.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      menuButton.setAttribute("aria-expanded", "false");
    });
  });
}

const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

const quoteForm = document.getElementById("quoteForm");
if (quoteForm) {
  quoteForm.addEventListener("submit", event => {
    event.preventDefault();
    const data = new FormData(quoteForm);
    const fields = [
      ["Name", data.get("name")],
      ["Phone", data.get("phone")],
      ["Email", data.get("email") || "Not provided"],
      ["Customer type", data.get("customerType")],
      ["Town", data.get("town")],
      ["Service", data.get("service")],
      ["Details", data.get("message") || "None provided"]
    ];
    const message = fields.map(([label, value]) => `${label}: ${value}`).join("\n");
    const feedback = quoteForm.querySelector(".form-feedback");
    feedback.textContent = "Your enquiry details are ready. The form needs the company's real email, WhatsApp number or form endpoint connected before it can send enquiries.";
    // For launch, connect this form to Formspree, Netlify Forms, or a verified WhatsApp number.
    console.info("Reste Propre enquiry draft:\n" + message);
  });
}
