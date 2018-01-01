let g_volume_value: number = 50;
let g_volume_next_value: number = 50;
let g_volume_timeout: number | null = null;

function volume_set_instantly(value)
{
    if (g_volume_value !== value)
    {
        g_volume_value = value;
        g_volume_next_value = value;

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/service/volume", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("action=" + g_volume_value.toString() + "%");
    }
}

function volume_timeout()
{
    volume_set_instantly(g_volume_value);
    g_volume_value = g_volume_next_value;
    g_volume_timeout = null;
}

function volume_set(value)
{
    g_volume_next_value = value;
    if (g_volume_timeout == null)
    {
        volume_set_instantly(g_volume_next_value);
        g_volume_timeout = setTimeout(volume_timeout, 150);
    }
}

function volume_get()
{
    return g_volume_next_value;
}

window.onload = function () {
    let volumeslider = (<HTMLInputElement> document.getElementById("volumeslider"));
    if (volumeslider)
    {
        volumeslider.addEventListener("input", function(){
            volume_set(volumeslider.value);
        });
        volumeslider.addEventListener("change", function(){
            volume_set_instantly(volumeslider.value);
        });

    }
};

/* EOF */
