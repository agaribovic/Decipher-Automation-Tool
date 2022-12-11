import React, { useState, useEffect } from 'react';

const GetApi = () => {

    const [products, setProducts] = useState([])

    const fetchData = () => {
      fetch("https://fakestoreapi.com/products")
        .then(response => {
          return response.json()
        })
        .then(data => {
            setProducts(data)
        })
    }
  
    useEffect(() => {
      fetchData()
    }, [])

    const deleteRow = (event) => {  

      let x = event.target;
        x.parentNode.parentNode.style.opacity = "1";
        if (x.parentNode.parentNode.className === "post") {              
          let intervalID;  
          const deletePost = () => { x.parentNode.parentNode.style.opacity -= "0.1"; }
          intervalID = setInterval(deletePost, 100)
      } 
    }  
  
    return (
      <div>
        {products.length > 0 && (
          <table>
            <tr>
                <th><h1>ID</h1></th>
                <th><h1>Title</h1></th>
                <th><h1>Price</h1></th>
                <th><h1>Action</h1></th>
            </tr>
            {products.map(product => (
              <tr key={product.id} className="post">
                  <td>{product.id}</td>
                  <td>{product.title}</td>
                  <td>{product.price}</td>
                  <td>
                  <button className="btn btn-danger" onClick={(event) => deleteRow(event)}>Delete</button>  
                  </td>
              </tr>
            ))}
          </table>
        )}
      </div>
    )
  }

export default GetApi;