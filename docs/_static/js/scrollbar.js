/*  When the user scrolls down, hide the navbar/version dropdown
    When the user scrolls up, show the navbar/version dropdown
*/

// TODO: Clean this up once dynamic components are finalized.

var prevScrollpos = window.pageYOffset;

window.onscroll = function() {

  const currentScrollPos = window.pageYOffset;
  const scroll_delta = currentScrollPos - prevScrollpos

  const e_header = document.getElementsByClassName("md-header");
  const has_e_header = e_header.length > 0

  const e_version = document.getElementsByClassName("rst-versions rst-badge");
  const has_e_version = e_version.length > 0

  // const e_content = document.getElementsByClassName("md-content");
  const e_content = document.getElementsByClassName("md-main");

  if (scroll_delta < 0) {

    if (has_e_header) {
        e_header[0].style.top = "0";
        e_header[0].style.display = "block";
        e_header[0].style.backgroundImage = "var(--sn-default-header)";

        // e_header[0].style.backgroundImage = "var(--sn-default-header)";

        // e_content[0].style.backgroundColor = "var(--sn-background-dark)";

        // e_content[0].style.backgroundColor = "#040d17";
        // e_header[0].style.display = "unset";
        // e_header[0].style.height = "3rem";
        // e_header[0].style.padding_top = "0.5em";
      }
    if (
        has_e_version
        && scroll_delta <= -30  /* allow for some scrolling up before re-appear */
    ) {
        e_version[0].style.display = "block";
      }

  } else {

    if (
        has_e_header           /* page has loaded/e_header have been found */
        && screen.width < 1100 /* only apply on screen size < 1100 px */
        && scroll_delta >= 20  /* allow for some scrolling down before collapse */
    ) {
        // e_header[0].style.display = "none";
        // e_header[0].style.height = "0";
        // e_header[0].style.padding_top = "0";
        e_header[0].style.top = "-3rem";

        // e_content[0].style.backgroundColor = "#040d17";

        // e_content[0].style.backgroundColor = "transparent";
      }
    else if (
        has_e_header           /* page has loaded/e_header have been found */
        && screen.width >= 1100 /* only apply on screen size < 1100 px */
        && scroll_delta >= 20  /* allow for some scrolling down before collapse */
    ) {
        // e_header[0].style.display = "none";
        e_header[0].style.backgroundImage = "var(--sn-focused-header)";

        // e_header[0].style.height = "0";
        // e_header[0].style.padding_top = "0";
        // e_header[0].style.top = "-3rem";


        // e_content[0].style.backgroundColor = "var(--sn-focused-background-dark)";

        // e_content[0].style.backgroundColor = "#040d17";
        // e_content[0].style.backgroundColor = "transparent";
      }
    if (
        has_e_version
        && scroll_delta >= 20
    ) {
        e_version[0].style.display = "none"
    }

  }

  prevScrollpos = currentScrollPos;

}
