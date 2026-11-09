package com.litagent.knowledge.entity;
import jakarta.persistence.*;
@Entity 
@Table (name="topics")
public class Topic {
    @Id
    @GeneratedValue(strategy=GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToOne 
    @JoinColumn(name="user_id")
    private User user;

    public void setName(String name){
        this.name=name;
    }
    public void setUser(User user){
        this.user=user;
    }

    public Long getId(){
        return id;
    }
    public String getName(){
        return name;
    }
    public User getUser(){
        return user;
    }
}
