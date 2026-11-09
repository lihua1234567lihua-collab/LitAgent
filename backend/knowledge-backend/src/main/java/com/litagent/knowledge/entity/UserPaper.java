
package com.litagent.knowledge.entity;
import jakarta.persistence.*;
@Entity 
@Table (name="user_papers",
        uniqueConstraints = {
        @UniqueConstraint(columnNames = {"user_id", "paper_id"})
    }
)
public class UserPaper {
    @Id 
    @GeneratedValue (strategy=GenerationType.IDENTITY)
    private Long id;

    @ManyToOne 
    @JoinColumn (name="user_id")
    private User user;

    @ManyToOne 
    @JoinColumn (name="paper_id")
    private Paper paper;

    public void setUser(User user){
        this.user=user;
    }
    public void setPaper(Paper paper){
        this.paper=paper;
    }

    public Long getId() {
    return id;
}

    public User getUser() {
        return user;
    }

    public Paper getPaper() {
        return paper;
    }

}
