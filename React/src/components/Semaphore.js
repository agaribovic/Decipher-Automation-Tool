import React, { useState } from 'react';

const Semaphore = () => {

  const [count, setCount] = useState(10);
  const [color, setColor] = useState("")
  const [visibility1, setVisibility1] = useState("hidden");
  const [visibility2, setVisibility2] = useState("hidden");
  const [visibility3, setVisibility3] = useState("hidden");
  const [input, setInput] = useState('')
  const error = "Please enter a valid color name."
  const colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple", "violet", "magenta", "red", "brown", "grey", "pink"]
  let colorFound = false 

  colors.forEach(color => {
    if(input.includes(color))
      colorFound = true
  })
 
  setTimeout(() => {

    if(count === 1)
      setCount(10)
    else 
      setCount(count - 1)

    if(count > 7) {
      setVisibility1("visible")
      setVisibility2("hidden")
      setVisibility3("hidden")
    } else if (count > 3) {
      setVisibility1("hidden")
      setVisibility2("visible")
      setVisibility3("hidden")
    } else {
      setVisibility1("hidden")
      setVisibility2("hidden")
      setVisibility3("visible")
    }
      
  }, 1000);



  return (
    <div id="semaphore"
    style= {{background: color}}
    >
      
      <div className="color" style={{visibility: visibility1}}></div>
      <div className="color" style={{visibility: visibility2}}></div>
      <div className="color" style={{visibility: visibility3}}></div>
     
      <br/>
      
      <input type="text"  
      style={{
         "textAlign": "center",
         "position": "relative",
         "height": "5%",
         "width": "60%",
         "top": "20%"
      }}
      onChange={(e) => setColor(e.target.value)}
      value={input} onInput={e => setInput(e.target.value)}
      placeholder={"Change color"}
      />

      <br/><br/><br/> 

    {input.length > 0 && (!colorFound) &&
      <p style=
        {{
        "color": "red",
        "font-weight": "bold",
        "textAlign": "center",
        "fontSize": "20px"
        }}
        >{error}
        </p>
    }
    
    </div>
  );
}

export default Semaphore;
