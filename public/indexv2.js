let world = "salocaia";
if (window.location.hash !== undefined && window.location.hash.length > 1) {
    world = window.location.hash.slice(1);
}

let world_cap = world.charAt(0).toUpperCase() + world.slice(1);
document.querySelector("#banner").textContent = `${world_cap} Statistics`

d3.queue()
  .defer(d3.json, `${world}_data_v2.json`)
  .await((error, d20_data) => {
    for (const [key, value] of Object.entries(d20_data["All"])) {
      document.querySelectorAll(`.all_${key}`).forEach((element) => element.textContent = value)
    }
});