let g_volume_value: number = 50;
let g_volume_next_value: number = 50;
let g_volume_timeout: number | null = null;

function volume_set_instantly(value: number)
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
    volume_set_instantly(g_volume_next_value);
    g_volume_timeout = null;
}

function volume_set(value: number)
{
    if (value < 0)
    {
        value = 0;
    }
    else if (value > 100)
    {
        value = 100;
    }

    g_volume_next_value = value;

    let volumeslider = (<HTMLInputElement> document.getElementById("volumeslider"));
    volumeslider.value = value.toString();

    if (g_volume_timeout == null)
    {
        volume_set_instantly(g_volume_next_value);
        g_volume_timeout = setTimeout(volume_timeout, 150);
    }
}

function volume_get(): number
{
    return g_volume_next_value;
}

window.onload = function () {
    let volumeslider = (<HTMLInputElement> document.getElementById("volumeslider"));
    if (volumeslider)
    {
        volumeslider.addEventListener("input", function(){
            volume_set(parseInt(volumeslider.value));
        });
        volumeslider.addEventListener("change", function(){
            volume_set_instantly(parseInt(volumeslider.value));
        });

    }

    let volume_up_button = (<HTMLButtonElement> document.getElementById("volumeup"));
    if (volume_up_button)
    {
        volume_up_button.addEventListener("click", function(){
            volume_set(volume_get() + 5);
        });
    }

    let volume_down_button = (<HTMLButtonElement> document.getElementById("volumedown"));
    if (volume_down_button)
    {
        volume_down_button.addEventListener("click", function(){
            volume_set(volume_get() - 5);
        });
    }
};

/* EOF */
