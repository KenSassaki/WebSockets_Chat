<script>
  export let name;
  import { onMount } from "svelte";

  let messageInput;
  let messages = [];
  let inputText = "";
  
  onMount(() => {
    messageInput.focus();
  });
  const ws = new WebSocket("ws://localhost:8765");

  ws.onopen = function () {
    console.log("WebSocket Client conectado");
  };

  ws.onmessage = function (e) {
    console.log("Received: " + e.data);
    messages = [...messages, e.data];
    inputText = "";
  };

  function handleClick() {
    ws.send(inputText);
    messages = [...messages, "Eu: " + inputText];
    messageInput = "";
    inputText = ""; 
  };


</script>

<style>
  * {
    box-sizing: border-box;
  }

  main {
    width: calc(100% - 30px);
    text-align: center;
    padding: 1em;
    max-width: 1240px;
    margin: 0 auto;
  }

  h1 {
    color: #8029DF;
    text-transform: uppercase;
    font-size: 4em;
    font-weight: 100;
  }

  .chatbox {
    width: 100%;
    height: 50vh;
    padding: 0 1em;
    text-align: left;
    background-color: #eee;
    overflow-y: scroll;
    overscroll-behavior-y: contain;
    scroll-snap-type: y proximity;
  }

  .chatbox p {
    margin-top: 0.5em;
    margin-bottom: 0;
    padding-bottom: 0.5em;
  }

  .chatbox > p:last-child {
    scroll-snap-align: end;
  }

  .inputbox {
    display: flex;
    margin-top: 0.5em;
  }

  .inputbox input {
    flex-grow: 1;
  }
</style>

<main>
  <h1>{"WebSockets Chat"}</h1>
  <p>
    When topics are complex and meaty, don't create a never-ending email thread. It's amazing how much time people waste composing and reading carefully-worded essays, when a WebSocket Chat would resolve the whole thing.
  </p>
  <div class="chatbox">
    {#each messages as message}
      <p>{message}</p>
    {/each}
  </div>
  <form class="inputbox">
    <input type="text" bind:this={messageInput} bind:value={inputText} />
    <button type="submit" on:click|preventDefault={handleClick}>Enviar</button>
  </form>
</main>
