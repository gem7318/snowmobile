DarkReader.setFetchMethod(window.fetch)

// Check if Dark Reader is enabled.
const isEnabled = DarkReader.isEnabled();

if (isEnabled === true) {
    DarkReader.disable()
}

// Then use style sheets

// if (isEnabled === false) {
//     DarkReader.enable({
//         brightness: 100,
//         contrast: 90,
//         sepia: 10
//     })
//
//     DarkReader.backgroundColor = "#02080e";

    // document.body.style.backgroundColor = "red";

    // const bod = document.getElementsByClassName("md-main");
    // const inner = document.getElementsByClassName("md-content");

    // if (bod.length > 0 && inner.length > 0) {
    //     bod[0].style.backgroundColor = "#02080e";
    //     inner[0].style.backgroundColor = "#02080e";
    // }
// }

// DarkReader.enable({
//     brightness: 100,
//     contrast: 90,
//     sepia: 10
// });


// DarkReader.disable();

// Enable when system color scheme is dark.
// DarkReader.auto({
//     brightness: 100,
//     contrast: 90,
//     sepia: 10
// });

// Stop watching for system color scheme.
// DarkReader.auto(false);

// Get the generated CSS of Dark Reader returned as a string.
// const CSS = DarkReader.exportGeneratedCSS();

// Check if Dark Reader is enabled.
// const isEnabled = DarkReader.isEnabled();

// if (isEnabled === false) {
    // const head = document.getElementsByClassName("md-header");
    // const head = document.getElementsByName("head");
    // if (head.length > 0) {
    //     head[0].style = CSS
    // }
// }
