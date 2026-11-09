package com.litagent.knowledge.service;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.repository.UserRepository;
import org.springframework.stereotype.Service;
import java.util.List;
@Service //告诉spring这是业务逻辑层
public class UserService {
    private final UserRepository userRepository;
    public UserService(UserRepository userRepository){
        this.userRepository=userRepository;
    }
    public List<User> findAll(){
        return userRepository.findAll();//查询user表里面的所有数据
    }
    public User createUser(User user){
        return userRepository.save(user);
    }
    public void deleteUser(long id){
        userRepository.deleteById(id);
    }
    public User updateUser(Long id, User newUser){
        User oldUser=userRepository.findById(id).orElseThrow();
        oldUser.setUsername(newUser.getUsername());
        return userRepository.save(oldUser);
    }
}
