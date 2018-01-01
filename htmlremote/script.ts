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

function make_key(key: string, text: string)
{
    let form = document.createElement("form");
    form.setAttribute("action", "/service/keyboard");
    form.setAttribute("method", "post");
    form.setAttribute("target", "frame");

    let button = document.createElement("button");
    button.setAttribute("class", "keyboardbutton");
    button.setAttribute("type", "submit");
    button.setAttribute("name", "action");
    button.setAttribute("value", "press");
    button.innerText = text;
    form.appendChild(button);

    let input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", "key");
    input.setAttribute("value", key);
    form.appendChild(input);

    let keyboard = document.getElementById("keyboard");
    if (keyboard != null)
    {
        keyboard.appendChild(form);
    }
}

function make_key_newline()
{
    let br = document.createElement("br");

    let keyboard = document.getElementById("keyboard");
    if (keyboard != null)
    {
        keyboard.appendChild(br);
    }
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

    let keys: (string|string[])[][] = [
        [ "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12" ],
        [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ["minus", "-"], ["equal", "="] ],
        [ "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", ["bracketleft", "["], ["bracketright", "]"] ],
        [ "a", "s", "d", "f", "g", "h", "j", "k", "l", ["semicolon", ";"], ["apostrophe", "'"] ],
        [ "z", "x", "c", "v", "b", "n", "m", ["comma", ","], ["period", "."], ["slash", "/"], ["backslash", "\\"] ],
    ];

    make_key_newline();
    for(let row of keys)
    {
        for(let key of row)
        {
            if (typeof key === 'string')
            {
                make_key(key, key);
            }
            else
            {
                make_key(key[0], key[1]);
            }
        }
        make_key_newline();
    }
};

/* EOF */