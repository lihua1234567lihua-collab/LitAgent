package com.litagent.knowledge.entity;
import jakarta.persistence.*;
@Entity 
@Table (name="users")
public class User{
    @Id 
    @GeneratedValue (strategy=GenerationType.IDENTITY)
    private Long id;
    private String username;
    public void setUsername(String username){
        this.username=username;
    }
    public Long getId(){
        return id;
    }
    public String getUsername(){
        return username;
    }
}

