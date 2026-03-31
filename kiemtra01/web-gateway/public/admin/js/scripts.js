document.addEventListener("DOMContentLoaded", () => {
  const sideNavToggle = document.getElementById("sidebarToggle");
  const sideNav = document.getElementById("layoutSidenav_nav");

  if (sideNavToggle && sideNav) {
    sideNavToggle.addEventListener("click", (event) => {
      event.preventDefault();
      sideNav.style.display = sideNav.style.display === "none" ? "block" : "none";
    });
  }
});
